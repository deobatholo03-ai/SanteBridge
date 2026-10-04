# SanteBridge — prototype conversationnel RDC

Application Flask existante enrichie d'un assistant patient français / lingala.
Après connexion, le patient arrive sur `/patient/assistant`.

## Lancer

Python 3.12. Installer `pip install -r requirements.txt`. Configurer `.env`
sur le modèle de `.env.example` (ne jamais committer une clé).
Il est également possible de définir `SANTEBRIDGE_ENV_FILE` avec le chemin
d'un fichier existant. Le serveur utilise OpenAI Responses et `gpt-4.1-mini`
par défaut, modifiable via `OPENAI_MODEL`.

`python -m flask --app run:app run --host 127.0.0.1 --port 5001 --no-reload`

La base SQLite est dans `instance/dev.db`. Ne pas lancer `seed_db.py` sur une
base à conserver : ce script historique supprime les données avant de peupler.

## Fonctionnement

- Compte patient obligatoire ; CSRF sur les envois et la suppression d'échange.
- Accord explicite à l'envoi des messages à OpenAI. Aucun nom de compte,
  téléphone ou dossier patient ajouté automatiquement aux requêtes.
- Historique en mémoire serveur, isolé par utilisateur et session, durée
  d'inactivité de 30 minutes (nettoyage à la prochaine requête), 12 échanges
  maximum, réinitialisation explicite. Pas de stockage navigateur des messages.
  Recharger la page masque les messages précédents ; utiliser « Effacer
  l'échange » pour supprimer aussi le contexte côté serveur.
- `store=false` désactive le stockage de la réponse pour récupération via API ;
  ce paramètre ne garantit pas à lui seul une absence totale de rétention par
  le fournisseur. Vérifier les conditions de traitement avant un pilote réel.
- Annuaire limité aux 100 premiers professionnels. Les cartes sont construites
  depuis la base, jamais à partir de liens générés. Réservation via le formulaire
  existant, aucun acte automatique de l'IA.
- Les stocks, horaires et diplômes ne sont pas vérifiés. Les données historiques
  peuvent être des démonstrations ivoiriennes, pas des partenaires en RDC.
- Aucune prescription ou posologie personnalisée. Les protocoles médicamenteux
  validés et le contrôle médical ne sont pas encore intégrés.

## Validation et limites

`python -m unittest discover -s tests -v`

Prototype local mono-processus. Avant utilisation par de vrais patients :
validation clinique et linguistique en lingala, évaluation des urgences et des
échecs du modèle, professionnels RDC vérifiés, HTTPS et authentification
renforcée, politique de données, stockage/limitation partagés si plusieurs
processus. Les instructions au modèle ne constituent pas une garantie de
sécurité médicale. L'interface et les erreurs de l'assistant sont bilingues ;
les anciennes pages restent en français. La voix n'est pas encore intégrée.
