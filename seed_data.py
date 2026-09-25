import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.doctor_patient import DoctorPatient
from app.auth.jwt import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Doctor).count() > 0:
            print("Database already has records.")
            return

        admin = db.query(User).filter(User.email == "admin@healthapp.com").first()
        if not admin:
            admin = User(
                email="admin@healthapp.com",
                hashed_password=hash_password("AdminPassword123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.flush()

        user_doc1 = User(
            email="dr.strange@healthapp.com",
            hashed_password=hash_password("Doctor@123"),
            role=UserRole.DOCTOR,
            is_active=True,
        )
        db.add(user_doc1)
        db.flush()

        doc1 = Doctor(
            name="Dr. Stephen Strange",
            specialization="Neuro Surgery",
            email="dr.strange@healthapp.com",
            is_active=True,
            user_id=user_doc1.id,
        )
        db.add(doc1)
        db.flush()

        user_doc2 = User(
            email="dr.house@healthapp.com",
            hashed_password=hash_password("Doctor@123"),
            role=UserRole.DOCTOR,
            is_active=True,
        )
        db.add(user_doc2)
        db.flush()

        doc2 = Doctor(
            name="Dr. Gregory House",
            specialization="Diagnostic Medicine",
            email="dr.house@healthapp.com",
            is_active=True,
            user_id=user_doc2.id,
        )
        db.add(doc2)
        db.flush()

        p1 = Patient(name="John Doe", age=34, phone="+12345678901", is_active=True)
        p2 = Patient(name="Jane Smith", age=29, phone="+19876543210", is_active=True)
        p3 = Patient(name="Robert Brown", age=52, phone="+11223344556", is_active=True)
        p4 = Patient(name="Emily Davis", age=41, phone="+15556667778", is_active=True)
        p5 = Patient(name="Michael Green", age=68, phone="+19998887776", is_active=True)

        db.add_all([p1, p2, p3, p4, p5])
        db.flush()

        a1 = DoctorPatient(doctor_id=doc1.id, patient_id=p1.id)
        a2 = DoctorPatient(doctor_id=doc1.id, patient_id=p2.id)
        a3 = DoctorPatient(doctor_id=doc2.id, patient_id=p3.id)
        a4 = DoctorPatient(doctor_id=doc2.id, patient_id=p4.id)

        db.add_all([a1, a2, a3, a4])
        db.commit()

        print("Seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
