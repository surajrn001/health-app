from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patients(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> Tuple[List[Patient], int]:
    query = db.query(Patient)

    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Patient.name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
            )
        )

    total = query.count()
    patients = query.order_by(Patient.id.asc()).offset(skip).limit(limit).all()
    return patients, total


def create_patient(db: Session, patient_in: PatientCreate) -> Patient:
    db_patient = Patient(
        name=patient_in.name.strip(),
        age=patient_in.age,
        phone=patient_in.phone.strip(),
        is_active=True,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient: Patient, patient_in: PatientUpdate) -> Patient:
    update_data = patient_in.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"]:
        patient.name = update_data["name"].strip()

    if "age" in update_data and update_data["age"] is not None:
        patient.age = update_data["age"]

    if "phone" in update_data and update_data["phone"]:
        patient.phone = update_data["phone"].strip()

    db.commit()
    db.refresh(patient)
    return patient
