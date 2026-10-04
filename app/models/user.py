# app/models/user.py
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="patient")
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Champs profil médecin
    specialty = db.Column(db.String(100), nullable=True)
    workplace = db.Column(db.String(200), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    photo_url = db.Column(db.String(255), nullable=True)
    
    # ⚠️ AUCUNE RELATION ICI pour éviter les conflits SQLAlchemy
    # Nous interrogerons directement via Appointment.query ou Prescription.query

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"