# app/models/prescription.py
from app.extensions import db
from datetime import datetime
import uuid

class Prescription(db.Model):
    __tablename__ = "prescriptions"
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    medications = db.Column(db.Text, nullable=False) 
    notes = db.Column(db.Text, nullable=True)
    qr_code = db.Column(db.String(64), unique=True, default=lambda: f"RX-{uuid.uuid4().hex[:12].upper()}")
    pharmacy_status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations simples (sans backref)
    appointment = db.relationship("Appointment")
    doctor = db.relationship("User", foreign_keys=[doctor_id])
    patient = db.relationship("User", foreign_keys=[patient_id])

    def __repr__(self):
        return f"<Prescription {self.qr_code}>"