import json
import unittest
from unittest.mock import patch
from app import create_app
from app.extensions import db
from app.models.user import User
from app.routes.assistant import _conversations
from app.services.assistant import AssistantUnavailable, respond


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only',
                              'SQLALCHEMY_DATABASE_URI': 'sqlite://', 'WTF_CSRF_ENABLED': False})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        for i, role in enumerate(['patient', 'patient', 'doctor', 'pharmacy'], 1):
            db.session.add(User(id=i, name=f'Example {i}', email=f'{i}@example.test',
                                role=role, password_hash='not-used', specialty='Gynécologue' if i == 3 else None))
        db.session.commit()
        self.ctx.pop()
        _conversations.clear()
        self.client = self.app.test_client()
        self.login(self.client, 1)

    def tearDown(self):
        self.ctx.push()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, client, user_id):
        with client.session_transaction() as session:
            session['_user_id'] = str(user_id)
            session['_fresh'] = True

    def post(self, **extra):
        return self.client.post('/patient/assistant/message', json={
            'message': 'Je cherche un gynécologue', 'language': 'fr', 'consent': True, **extra})

    @patch('app.routes.assistant.respond')
    def test_cards_are_from_database_and_cannot_target_patient(self, mock):
        mock.return_value = {'reply': 'Voici un médecin.', 'urgent': False, 'provider_ids': [1, 3, 999]}
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p['name'] for p in response.json['providers']], ['Example 3'])
        self.assertEqual(response.json['providers'][0]['url'], '/patient/book/3')
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    @patch('app.routes.assistant.respond')
    def test_urgent_suppresses_booking_cards(self, mock):
        mock.return_value = {'reply': 'Cherchez une aide immédiate.', 'urgent': True, 'provider_ids': [3]}
        self.assertEqual(self.post().json['providers'], [])

    @patch('app.routes.assistant.respond')
    def test_validation_and_consent_before_api(self, mock):
        for extra in [{'consent': False}, {'language': 'en'}, {'message': ' '}, {'message': 'x'*2001}]:
            self.assertEqual(self.post(**extra).status_code, 400)
        self.assertEqual(self.client.post('/patient/assistant/message', json=[]).status_code, 400)
        mock.assert_not_called()

    @patch('app.routes.assistant.respond')
    def test_identity_and_rate_limit(self, mock):
        mock.return_value = {'reply': 'Bonjour', 'urgent': False, 'provider_ids': []}
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(self.post().status_code, 429)
        self.login(self.client, 3)
        self.assertEqual(self.post().status_code, 403)
        self.assertEqual(self.app.test_client().post('/patient/assistant/message', json={}).status_code, 401)

    @patch('app.routes.assistant.respond')
    def test_history_is_server_side_scoped_and_resettable(self, mock):
        mock.return_value = {'reply': 'Bonjour', 'urgent': False, 'provider_ids': []}
        self.post(message='Private synthetic symptom')
        with self.client.session_transaction() as session:
            self.assertNotIn('Private synthetic symptom', str(dict(session)))
        other = self.app.test_client()
        self.login(other, 2)
        other.post('/patient/assistant/message', json={'message': 'Mbote', 'language': 'ln', 'consent': True})
        self.assertEqual(mock.call_args.args[0], [{'role': 'user', 'content': 'Mbote'}])
        self.assertEqual(mock.call_args.args[1], 'ln')
        self.assertEqual(self.client.post('/patient/assistant/reset', json={}).status_code, 200)
        self.assertEqual(len(_conversations), 1)

    @patch('app.routes.assistant.respond', side_effect=AssistantUnavailable('http_429'))
    def test_provider_failure_is_safe_and_retryable(self, mock):
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {'error': 'unavailable'})
        state = next(iter(_conversations.values()))
        self.assertFalse(state['busy'])
        self.assertEqual(state['messages'], [])

    def test_csrf_and_page(self):
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.assertEqual(self.post().status_code, 400)
        response = self.client.get('/patient/assistant')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-csrf=', response.data)

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'synthetic-test-key'})
    @patch('app.services.assistant.urlopen')
    def test_adapter_requests_structured_output_without_storage(self, mock):
        body = {'status': 'completed', 'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': json.dumps({'reply': 'Mbote', 'urgent': False, 'provider_ids': []})}]}]}
        mock.return_value.__enter__.return_value.read.return_value = json.dumps(body)
        result = respond([{'role': 'user', 'content': 'Mbote'}], 'ln', [])
        self.assertEqual(result['reply'], 'Mbote')
        payload = json.loads(mock.call_args.args[0].data)
        self.assertFalse(payload['store'])
        self.assertTrue(payload['text']['format']['strict'])


if __name__ == '__main__':
    unittest.main()
