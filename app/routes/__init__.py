# app/routes/__init__.py
from app.routes.auth import auth_bp
from app.routes.patient import patient_bp
from app.routes.doctor import doctor_bp
from app.routes.pharmacy import pharmacy_bp

def register_routes(app):
    from app.routes.assistant import assistant_bp
    app.register_blueprint(assistant_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(pharmacy_bp)
