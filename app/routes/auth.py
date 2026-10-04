# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "patient")
        phone = request.form.get("phone")
        
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return redirect(url_for("auth.register"))
        
        new_user = User(name=name, email=email, role=role, phone=phone)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Compte créé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f"Bienvenue {user.name} !", "success")
            
            # Redirection intelligente selon le rôle (Indentation corrigée ici)
            if user.role == "doctor":
                return redirect(url_for("doctor.dashboard"))
            elif user.role == "pharmacy":
                return redirect(url_for("pharmacy.dashboard"))
            elif user.role == "diagnostic":
                return redirect(url_for("diagnostic.dashboard"))
            else:
                return redirect(url_for("assistant.page"))
        
        flash("Email ou mot de passe incorrect.", "danger")
    
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for("auth.login"))
