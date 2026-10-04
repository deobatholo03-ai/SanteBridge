# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Configuration de Flask-Login
login_manager.login_view = "auth.login"
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"