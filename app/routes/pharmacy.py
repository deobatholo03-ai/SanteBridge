# app/routes/pharmacy.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.extensions import db
from app.models.prescription import Prescription

pharmacy_bp = Blueprint("pharmacy", __name__, url_prefix="/pharmacy")

@pharmacy_bp.route("/dashboard")
@login_required
@role_required("pharmacy")
def dashboard():
    # Affiche les 10 dernières ordonnances pour la démo
    recent_rx = Prescription.query.order_by(Prescription.created_at.desc()).limit(10).all()
    return render_template("pharmacy/dashboard.html", prescriptions=recent_rx)

@pharmacy_bp.route("/verify", methods=["GET", "POST"])
@login_required
@role_required("pharmacy")
def verify():
    rx = None
    if request.method == "POST":
        rx_code = request.form.get("rx_code", "").strip().upper()
        rx = Prescription.query.filter_by(qr_code=rx_code).first()
        
        if not rx:
            flash("❌ Ordonnance introuvable. Vérifiez le code QR.", "danger")
        elif rx.pharmacy_status == "delivered":
            flash("⚠️ Cette ordonnance a déjà été livrée au patient.", "warning")
            
    return render_template("pharmacy/verify.html", rx=rx)

@pharmacy_bp.route("/process/<int:rx_id>", methods=["POST"])
@login_required
@role_required("pharmacy")
def process(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    action = request.form.get("action")
    
    if action == "prepare":
        rx.pharmacy_status = "prepared"
        flash("✅ Ordonnance marquée comme PRÉPARÉE. Prête pour le retrait/livraison.", "success")
    elif action == "deliver":
        rx.pharmacy_status = "delivered"
        flash("🚚 Ordonnance marquée comme LIVRÉE au patient.", "success")
        
    db.session.commit()
    return redirect(url_for("pharmacy.verify")) # Retourne à la page de vérification