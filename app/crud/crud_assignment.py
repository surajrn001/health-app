from typing import Tuple, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.doctor_patient import DoctorPatient


def assign_patient_to_doctor(
    db: Session,
    doctor_id: int,
    patient_id: int,
) -> Tuple[Doctor, Patient, DoctorPatient]:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign patient to deactivated doctor {doctor.name}",
        )

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )
    if not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign deactivated patient {patient.name}",
        )

    existing = (
        db.query(DoctorPatient)
        .filter(DoctorPatient.doctor_id == doctor_id, DoctorPatient.patient_id == patient_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient '{patient.name}' is already assigned to Doctor '{doctor.name}'",
        )

    assignment = DoctorPatient(doctor_id=doctor_id, patient_id=patient_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return doctor, patient, assignment


def get_doctor_patients(
    db: Session,
    doctor_id: int,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Patient], int]:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )

    query = (
        db.query(Patient)
        .join(DoctorPatient, DoctorPatient.patient_id == Patient.id)
        .filter(DoctorPatient.doctor_id == doctor_id)
    )

    total = query.count()
    patients = query.order_by(Patient.id.asc()).offset(skip).limit(limit).all()
    return patients, total


def is_patient_assigned_to_doctor(
    db: Session,
    doctor_id: int,
    patient_id: int,
) -> bool:
    return (
        db.query(DoctorPatient)
        .filter(DoctorPatient.doctor_id == doctor_id, DoctorPatient.patient_id == patient_id)
        .first()
        is not None
    )
