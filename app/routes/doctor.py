# app/routes/doctor.py
import qrcode
import base64
import io
import json
import uuid  # <-- AJOUTÉ pour uuid.uuid4()
from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.extensions import db  # <-- AJOUTÉ pour db.session
from app.models.appointment import Appointment
from app.models.prescription import Prescription # <-- AJOUTÉ pour le modèle

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")

# ... (le reste de ton code pour le dashboard et prescribe reste inchangé)

@doctor_bp.route("/dashboard")
@login_required
@role_required("doctor")
def dashboard():
    # Récupérer les RDV du médecin, triés par date et heure
    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).order_by(Appointment.date.asc(), Appointment.time_slot.asc()).all()
    
    # Passer la date d'aujourd'hui au template pour le filtre Jinja
    today_date = date.today()
    
    return render_template("doctor/dashboard.html", appointments=appointments, today_date=today_date)

@doctor_bp.route("/prescribe/<int:appointment_id>", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def prescribe(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    
    # Sécurité : vérifier que le RDV appartient bien à ce médecin
    if appt.doctor_id != current_user.id:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("doctor.dashboard"))

    if request.method == "POST":
        medications_text = request.form.get("medications", "").strip()
        notes = request.form.get("notes", "").strip()
        
        if not medications_text:
            flash("Veuillez ajouter au moins un médicament.", "warning")
            return redirect(request.url)
        
        # Générer un QR Code unique
        qr_data = f"https://santebridge.app/verify/{uuid.uuid4().hex[:12].upper()}" # URL de vérification future
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir l'image en base64 pour l'afficher directement dans le HTML
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Sauvegarder en base de données
        new_rx = Prescription(
            appointment_id=appt.id,
            doctor_id=current_user.id,
            patient_id=appt.patient_id,
            medications=medications_text,
            notes=notes,
            qr_code=qr_data.split('/')[-1] # On garde juste l'ID unique
        )
        db.session.add(new_rx)
        db.session.commit()
        
        # Mettre à jour le statut du RDV
        appt.status = "completed"
        db.session.commit()
        
        # Rediriger vers la vue de l'ordonnance générée
        return redirect(url_for("doctor.view_prescription", rx_id=new_rx.id))

    return render_template("doctor/prescribe.html", appt=appt)


@doctor_bp.route("/prescription/<int:rx_id>")
@login_required
@role_required("doctor")
def view_prescription(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    
    # Régénérer le QR code pour l'affichage
    qr_data = f"https://santebridge.app/verify/{rx.qr_code}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return render_template("doctor/view_prescription.html", rx=rx, qr_base64=qr_base64)