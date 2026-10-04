# app/models/appointment.py
from app.extensions import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = "appointments"
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations simples (sans backref)
    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("User", foreign_keys=[doctor_id])

    def __repr__(self):
        return f"<Appointment {self.date} {self.time_slot}>"