# app/utils/decorators.py
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*allowed_roles):
    """
    Décorateur qui restreint l'accès à une route selon le rôle.
    Usage : @role_required("patient", "doctor")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Veuillez vous connecter.", "warning")
                return redirect(url_for("auth.login"))
            
            if current_user.role not in allowed_roles:
                flash("Accès non autorisé pour votre rôle.", "danger")
                return redirect(url_for("auth.login"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator