# app/routes/patient.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.extensions import db
from app.models.user import User
from app.models.appointment import Appointment
from datetime import datetime

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")

@patient_bp.route("/dashboard")
@login_required
@role_required("patient")
def dashboard():
    # Récupérer les prochains RDV du patient
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=current_user.id,
        status="pending"
    ).order_by(Appointment.date.asc(), Appointment.time_slot.asc()).all()
    
    return render_template("patient/dashboard.html", appointments=upcoming_appointments)

@patient_bp.route("/search")
@login_required
@role_required("patient")
def search_doctors():
    # Récupérer tous les médecins
    doctors = User.query.filter_by(role="doctor").all()
    return render_template("patient/search_doctors.html", doctors=doctors)

@patient_bp.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@login_required
@role_required("patient")
def book_appointment(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    
    if request.method == "POST":
        date_str = request.form.get("date")
        time_slot = request.form.get("time_slot")
        reason = request.form.get("reason", "").strip()
        
        # Validation basique
        if not date_str or not time_slot:
            flash("Veuillez remplir la date et l'heure.", "danger")
            return redirect(request.url)
        
        try:
            appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Format de date invalide.", "danger")
            return redirect(request.url)
        
        # Vérifier que le créneau n'est pas déjà pris
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            time_slot=time_slot
        ).first()
        
        if existing:
            flash("Ce créneau est déjà réservé. Veuillez en choisir un autre.", "warning")
            return redirect(request.url)
        
        # Créer le rendez-vous
        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            date=appointment_date,
            time_slot=time_slot,
            reason=reason,
            status="pending"
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash(f"✅ Rendez-vous réservé avec {doctor.name} le {appointment_date} à {time_slot}", "success")
        return redirect(url_for("patient.dashboard"))
    
    return render_template("patient/book_appointment.html", doctor=doctor)

@patient_bp.route("/my-appointments")
@login_required
@role_required("patient")
def my_appointments():
    appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    
    return render_template("patient/my_appointments.html", appointments=appointments)
# ... (tes autres routes patient)

@patient_bp.route("/emergency")
@login_required
@role_required("patient")
def emergency():
    """Page de recherche d'ambulance d'urgence"""
    return render_template("patient/emergency.html")
@patient_bp.route("/prescription/<int:rx_id>")
@login_required
@role_required("patient")
def view_my_prescription(rx_id):
    from app.models.prescription import Prescription
    rx = Prescription.query.get_or_404(rx_id)
    
    # Sécurité : vérifier que l'ordonnance appartient bien à ce patient
    if rx.patient_id != current_user.id:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("patient.dashboard"))
    
    return render_template("patient/view_prescription.html", rx=rx)