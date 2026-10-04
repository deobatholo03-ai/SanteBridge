# run.py
from app import create_app
from app.extensions import db

app = create_app()

# Créer la base de données et les tables au premier lancement
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    print("🚀 SanteBridge démarre sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000)