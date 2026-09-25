import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.doctor_patient import DoctorPatient
from app.auth.dependencies import get_current_user, get_doctor_profile
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientDetailResponse,
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.crud.crud_patient import (
    get_patient,
    get_patients,
    create_patient,
    update_patient,
)
from app.crud.crud_assignment import (
    get_doctor_patients,
    is_patient_assigned_to_doctor,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


def _calculate_meta(total: int, page: int, page_size: int) -> PaginationMeta:
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginationMeta(
        total_items=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1 and total_pages > 0,
    )


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_new_patient(
    patient_in: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = create_patient(db, patient_in)

    if current_user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(current_user, db)
        if doctor and doctor.is_active:
            assignment = DoctorPatient(doctor_id=doctor.id, patient_id=patient.id)
            db.add(assignment)
            db.commit()

    return patient


@router.get("", response_model=PaginatedResponse[PatientResponse])
def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size

    if current_user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(current_user, db)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )
        patients, total = get_doctor_patients(db, doctor_id=doctor.id, skip=skip, limit=page_size)
    else:
        patients, total = get_patients(
            db,
            skip=skip,
            limit=page_size,
            is_active=is_active,
            search=search,
        )

    return PaginatedResponse(
        items=patients,
        meta=_calculate_meta(total, page, page_size),
    )


@router.get("/{patient_id}", response_model=PatientDetailResponse)
def get_patient_by_id(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )

    if current_user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(current_user, db)
        if not doctor or not is_patient_assigned_to_doctor(db, doctor.id, patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only view their own assigned patients",
            )

    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient_by_id(
    patient_id: int,
    patient_in: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )

    if current_user.role == UserRole.DOCTOR:
        doctor = get_doctor_profile(current_user, db)
        if not doctor or not is_patient_assigned_to_doctor(db, doctor.id, patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only update their own assigned patients",
            )

    return update_patient(db, patient, patient_in)
