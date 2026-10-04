(() => {
  'use strict';
  const root = document.querySelector('#assistant-app');
  const $ = id => document.getElementById(id);
  const copy = {
    fr: {
      title: 'Votre santé, parlons-en.', intro: 'Un premier échange pour trouver le bon accompagnement.',
      doctors: 'Trouver un médecin ↗', appointments: 'Mes rendez-vous ↗', dashboard: 'Mon espace patient ↗',
      prototype: 'Version de test. L’orientation médicale et le lingala doivent être validés par des soignants avant une utilisation réelle.',
      assistant: 'Assistant SanteBridge', subtitle: 'Orientation · Médecins · Pharmacies', language: 'Langue',
      safety: 'En cas de danger immédiat, cherchez une aide médicale sur place sans attendre une réponse ici. Cet assistant ne pose pas de diagnostic.',
      suggestDoctor: 'Trouver un gynécologue', suggestPharmacy: 'Contacter une pharmacie', suggestSymptoms: 'Parler de mes symptômes',
      consent: 'J’accepte l’envoi de cet échange à OpenAI pour obtenir une réponse. Je n’indique ni nom complet ni coordonnées. L’échange est conservé temporairement en mémoire sur ce serveur.',
      messageLabel: 'Votre message', send: 'Envoyer →', reset: 'Effacer l’échange', placeholder: 'Comment puis-je vous aider ?',
      welcome: 'Bonjour ! Je suis l’assistant IA de SanteBridge. Je peux vous aider à trouver un médecin, contacter une pharmacie ou comprendre la prochaine étape face à vos symptômes. De quoi avez-vous besoin ?',
      doctor: 'Je cherche un gynécologue en RDC.', pharmacy: 'Je cherche une pharmacie pour vérifier un produit.', symptoms: 'Je voudrais parler de mes symptômes.',
      waiting: 'L’assistant prépare sa réponse…', consentNeeded: 'Veuillez accepter l’envoi de cet échange avant de continuer.',
      unavailable: 'L’assistant est indisponible. Réessayez plus tard ou utilisez « Trouver un médecin ». En cas d’urgence, cherchez une aide médicale sur place.',
      auth: 'Votre session a expiré. Reconnectez-vous puis réessayez.', busy: 'Une demande est en cours. Patientez quelques secondes.',
      limit: 'Cet échange a atteint sa limite. Effacez-le pour commencer une nouvelle conversation.',
      invalid: 'Vérifiez votre message (2 000 caractères maximum).', book: 'Choisir un rendez-vous →',
      stock: 'Stock non connecté : disponibilité du produit à confirmer auprès de la pharmacie.',
      unknown: 'Établissement non renseigné', appointmentNote: 'Créneau à choisir et confirmer sur la page de réservation.',
    },
    ln: {
      title: 'Tólobela bokolɔngɔnɔ na yo.', intro: 'Tósolola mpo na koluka lisalisi oyo ebongi.',
      doctors: 'Koluka monganga ↗', appointments: 'Bokutani na ngai ↗', dashboard: 'Esika na ngai ↗',
      prototype: 'Ezali version ya komeka. Minganga oyo balobaka lingala basengeli naino kotala malamu biyano mpe mabongoli.',
      assistant: 'Mosungi SanteBridge', subtitle: 'Lisalisi · Minganga · Bafarmasi', language: 'Lokota',
      safety: 'Soki ozali na likama sikoyo, luka lisalisi ya monganga mbala moko. Kozela eyano awa te. Mosungi oyo akoki te kondimisa maladi na yo.',
      suggestDoctor: 'Koluka monganga ya basi', suggestPharmacy: 'Kosolola na farmasi', suggestSymptoms: 'Kolobela mpasi na ngai',
      consent: 'Nandimi kotinda masolo oyo na OpenAI mpo na kozwa eyano. Nakotya kombo na ngai mobimba to nimero ya telefone te. Masolo ekotikala mpo na mwa ntango na mémoire ya serveur oyo.',
      messageLabel: 'Nsango na yo', send: 'Tinda →', reset: 'Longola masolo', placeholder: 'Nakoki kosalisa yo ndenge nini ?',
      welcome: 'Mbote! Nazali mosungi IA ya SanteBridge. Nakoki kosalisa yo koluka monganga, kosolola na farmasi to koyeba litambe oyo okoki kolanda mpo na mpasi na yo. Ozali na mposa ya nini ?',
      doctor: 'Nazali koluka monganga ya basi na RDC.', pharmacy: 'Nazali koluka farmasi mpo na kotuna soki nkisi ezali.', symptoms: 'Nalingi kolobela mpasi na ngai.',
      waiting: 'Mosungi azali kobongisa eyano…', consentNeeded: 'Ndima naino kotinda masolo oyo liboso ya kokoba.',
      unavailable: 'Mosungi azali kosala te sikoyo. Meka lisusu sima to luka monganga. Soki ezali likama, luka lisalisi ya monganga mbala moko.',
      auth: 'Bokɔti na yo esili. Kɔta lisusu.', busy: 'Zela mwa moke, eyano ezali koya.',
      limit: 'Masolo oyo ekómi na ndelo. Longola yango mpo na kobanda masolo ya sika.',
      invalid: 'Tala nsango na yo (bilembo koleka 2 000 te).', book: 'Pona mokolo ya kokutana →',
      stock: 'Toyebi te soki nkisi ezali. Tuna na farmasi mpo na kondimisa.',
      unknown: 'Esika epesami te', appointmentNote: 'Pona mpe ndima ngonga na lokasa ya bokutani.',
    }
  };
  let busy = false;
  let welcome;
  const t = key => copy[$('language').value][key] || copy.fr[key];
  function bubble(text, role, urgent = false) {
    const node = document.createElement('div');
    node.className = `chat-message ${role}${urgent ? ' urgent' : ''}`;
    node.textContent = text;
    $('messages').append(node);
    node.scrollIntoView({block: 'nearest'});
    return node;
  }
  function translate() {
    root.lang = $('language').value;
    root.querySelectorAll('[data-i18n]').forEach(node => { node.textContent = t(node.dataset.i18n); });
    $('message').placeholder = t('placeholder');
    if (welcome) welcome.textContent = t('welcome');
  }
  function setBusy(value) {
    busy = value;
    ['send', 'reset', 'language', 'message', 'consent'].forEach(id => { $(id).disabled = value; });
    root.querySelectorAll('[data-prompt]').forEach(node => { node.disabled = value; });
    $('messages').setAttribute('aria-busy', String(value));
  }
  async function post(url, data) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 45000);
    try {
      const response = await fetch(url, {method: 'POST', credentials: 'same-origin', signal: controller.signal,
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': root.dataset.csrf}, body: JSON.stringify(data)});
      const result = await response.json().catch(() => ({error: response.status === 400 ? 'auth' : 'unavailable'}));
      if (!response.ok) throw new Error(result.error || 'unavailable');
      return result;
    } finally { clearTimeout(timer); }
  }
  $('language').addEventListener('change', translate);
  root.querySelectorAll('[data-prompt]').forEach(node => node.addEventListener('click', () => {
    $('message').value = t(node.dataset.prompt); $('message').focus();
  }));
  $('chat-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    if (!$('consent').checked) { $('status').textContent = t('consentNeeded'); $('consent').focus(); return; }
    const message = $('message').value.trim();
    if (!message) return;
    setBusy(true); $('status').textContent = t('waiting');
    const userBubble = bubble(message, 'user');
    try {
      const result = await post(root.dataset.messageUrl, {message, language: $('language').value, consent: true});
      const answer = bubble(result.reply, 'assistant', result.urgent);
      for (const provider of result.providers) {
        const card = document.createElement('div'); card.className = 'provider-card';
        const name = document.createElement('strong'); name.textContent = provider.name; card.append(name);
        const detail = document.createElement('p'); detail.textContent = [provider.specialty, provider.workplace || t('unknown')].filter(Boolean).join(' · '); card.append(detail);
        const note = document.createElement('p'); note.textContent = t(provider.role === 'doctor' ? 'appointmentNote' : 'stock'); card.append(note);
        if (provider.url && provider.url.startsWith('/patient/book/')) {
          const link = document.createElement('a'); link.href = provider.url; link.textContent = t('book'); card.append(link);
        }
        if (provider.phone) { const phone = document.createElement('p'); phone.textContent = provider.phone; card.append(phone); }
        answer.append(card);
      }
      $('message').value = ''; $('status').textContent = ''; $('suggestions').hidden = true;
      answer.scrollIntoView({block: 'nearest'});
    } catch (error) {
      userBubble.remove(); $('status').textContent = t(error.message) || t('unavailable');
    } finally { setBusy(false); $('message').focus(); }
  });
  $('reset').addEventListener('click', async () => {
    if (busy) return;
    setBusy(true);
    try {
      await post(root.dataset.resetUrl, {}); $('messages').replaceChildren();
      welcome = bubble(t('welcome'), 'assistant'); $('status').textContent = '';
      $('message').value = ''; $('suggestions').hidden = false;
    } catch { $('status').textContent = t('unavailable'); }
    finally { setBusy(false); }
  });
  translate(); welcome = bubble(t('welcome'), 'assistant');
})();
