# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, login_manager, csrf

# Charger les variables d'environnement (.env)
load_dotenv(os.getenv("SANTEBRIDGE_ENV_FILE") or None)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # 1. S'assurer que le dossier instance existe
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # 2. Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret")
    db_path = os.path.join(app.instance_path, "dev.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.update(MAX_CONTENT_LENGTH=24000, SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Lax")
    if test_config:
        app.config.update(test_config)
    
    # 3. Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # 4. 🔑 USER LOADER (CE QUI MANQUAIT !)
    # Cette fonction dit à Flask-Login comment retrouver un utilisateur par son ID
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))
    
    # 5. Enregistrement des routes
    from app.routes import register_routes
    register_routes(app)
    
    # 6. Route racine
    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))

    return app
