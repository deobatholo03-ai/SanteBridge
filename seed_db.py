# seed_db.py
import sys, os, uuid
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription

def seed_database():
    app = create_app()
    with app.app_context():
        # 🔑 CRÉER LES TABLES AVANT TOUTE CHOSE
        print("🏗️  Création des tables dans la base de données...")
        db.create_all()
        
        print("🗑️  Nettoyage de la base de données...")
        Prescription.query.delete()
        Appointment.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("👥 Création des utilisateurs avec profils détaillés...")
        
        # MÉDECINS (avec photos, spécialités, expériences)
        doctors = [
            User(
                name="Dr. Amadou Koffi", email="koffi@santebridge.com", role="doctor", phone="+225 07 07 07 01",
                specialty="Médecin Généraliste", workplace="Polyclinique Sainte Anne, Plateau",
                experience_years=12, is_online=True,
                photo_url="https://ui-avatars.com/api/?name=Amadou+Koffi&background=0D8ABC&color=fff&size=256"
            ),
            User(
                name="Dr. Fatou Diallo", email="fatou@santebridge.com", role="doctor", phone="+225 05 05 05 02",
                specialty="Pédiatre", workplace="Clinique des 2 Plateaux, Cocody",
                experience_years=8, is_online=True,
                photo_url="https://ui-avatars.com/api/?name=Fatou+Diallo&background=E11D48&color=fff&size=256"
            ),
            User(
                name="Dr. Jean-Baptiste Ouédraogo", email="jb@santebridge.com", role="doctor", phone="+225 01 01 01 03",
                specialty="Cardiologue", workplace="Hôpital Général de Bingerville",
                experience_years=20, is_online=False,
                photo_url="https://ui-avatars.com/api/?name=Jean+Baptiste&background=059669&color=fff&size=256"
            ),
        ]
        for doc in doctors:
            doc.set_password("medecin123")
            db.session.add(doc)
        
        # PATIENTS
        patients = [
            User(name="Marie Kouassi", email="marie@santebridge.com", role="patient", phone="+225 07 12 34 56"),
            User(name="Ibrahim Touré", email="ibrahim@santebridge.com", role="patient", phone="+225 05 98 76 54"),
        ]
        for pat in patients:
            pat.set_password("patient123")
            db.session.add(pat)
            
        # PHARMACIES
        pharmacies = [
            User(name="Pharmacie du Plateau", email="plateau@santebridge.com", role="pharmacy", phone="+225 27 20 20 20"),
        ]
        for ph in pharmacies:
            ph.set_password("pharma123")
            db.session.add(ph)
            
        db.session.commit()
        
        # RENDEZ-VOUS & ORDONNANCES
        today = date.today()
        appt1 = Appointment(patient_id=patients[0].id, doctor_id=doctors[0].id, date=today, time_slot="10:00", reason="Fièvre et maux de tête", status="pending")
        db.session.add(appt1)
        db.session.commit()
        
        rx1 = Prescription(appointment_id=appt1.id, doctor_id=doctors[0].id, patient_id=patients[0].id,
                          medications="- Paracétamol 1000mg : 1 comprimé 3 fois par jour.\n- Vitamine C : 1 comprimé le matin.",
                          notes="Repos et hydratation.", qr_code=f"RX-{uuid.uuid4().hex[:12].upper()}", pharmacy_status="pending")
        db.session.add(rx1)
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 BASE DE DONNÉES PRÊTE AVEC PROFILS MÉDECINS COMPLETS !")
        print("="*60)
        print("\n👨‍⚕️ MÉDECINS (mdp: medecin123)")
        print("   • koffi@santebridge.com (Généraliste, En ligne)")
        print("   • fatou@santebridge.com (Pédiatre, En ligne)")
        print("   • jb@santebridge.com (Cardiologue, Hors ligne)")
        print("\n👤 PATIENTS (mdp: patient123)")
        print("   • marie@santebridge.com")
        print("\n💊 PHARMACIE (mdp: pharma123)")
        print("   • plateau@santebridge.com")
        print("="*60)

if __name__ == "__main__":
    seed_database()