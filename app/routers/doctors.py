import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.dependencies import (
    get_current_user,
    require_admin,
    get_doctor_profile,
)
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorDetailResponse,
)
from app.schemas.patient import PatientResponse
from app.schemas.assignment import DoctorPatientAssignmentResponse
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.crud.crud_doctor import (
    get_doctor,
    get_doctor_by_email,
    get_doctors,
    create_doctor,
    update_doctor,
    soft_delete_doctor,
)
from app.crud.crud_assignment import (
    assign_patient_to_doctor,
    get_doctor_patients,
)

router = APIRouter(prefix="/doctors", tags=["Doctors"])


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


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_new_doctor(
    doctor_in: DoctorCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if get_doctor_by_email(db, doctor_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor with email '{doctor_in.email}' already exists",
        )
    return create_doctor(db, doctor_in)


@router.get("", response_model=PaginatedResponse[DoctorResponse])
def list_doctors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    specialization: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    doctors, total = get_doctors(
        db,
        skip=skip,
        limit=page_size,
        is_active=is_active,
        search=search,
        specialization=specialization,
    )
    return PaginatedResponse(
        items=doctors,
        meta=_calculate_meta(total, page, page_size),
    )


@router.get("/{doctor_id}", response_model=DoctorDetailResponse)
def get_doctor_by_id(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )
    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor_by_id(
    doctor_id: int,
    doctor_in: DoctorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )

    if current_user.role == UserRole.DOCTOR:
        user_doctor = get_doctor_profile(current_user, db)
        if not user_doctor or user_doctor.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile",
            )
        if doctor_in.is_active is not None and doctor_in.is_active != doctor.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can modify active status",
            )

    if doctor_in.email and doctor_in.email.lower().strip() != doctor.email.lower():
        existing = get_doctor_by_email(db, doctor_in.email)
        if existing and existing.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{doctor_in.email}' is already in use",
            )

    return update_doctor(db, doctor, doctor_in)


@router.delete("/{doctor_id}", response_model=DoctorResponse)
def delete_doctor(
    doctor_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found",
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor with id {doctor_id} is already deactivated",
        )

    return soft_delete_doctor(db, doctor)


@router.post("/{doctor_id}/patients/{patient_id}", response_model=DoctorPatientAssignmentResponse)
def assign_patient(
    doctor_id: int,
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.DOCTOR:
        user_doctor = get_doctor_profile(current_user, db)
        if not user_doctor or user_doctor.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only assign patients to themselves",
            )

    doctor, patient, assignment = assign_patient_to_doctor(db, doctor_id, patient_id)
    return DoctorPatientAssignmentResponse(
        message="Patient assigned successfully to doctor",
        doctor_id=doctor.id,
        doctor_name=doctor.name,
        patient_id=patient.id,
        patient_name=patient.name,
        assigned_at=assignment.assigned_at,
    )


@router.get("/{doctor_id}/patients", response_model=PaginatedResponse[PatientResponse])
def fetch_doctor_patients(
    doctor_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.DOCTOR:
        user_doctor = get_doctor_profile(current_user, db)
        if not user_doctor or user_doctor.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only view their own assigned patients",
            )

    skip = (page - 1) * page_size
    patients, total = get_doctor_patients(db, doctor_id=doctor_id, skip=skip, limit=page_size)
    return PaginatedResponse(
        items=patients,
        meta=_calculate_meta(total, page, page_size),
    )
