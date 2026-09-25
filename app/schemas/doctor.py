from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class DoctorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    specialization: str = Field(..., min_length=2, max_length=150)
    email: EmailStr


class DoctorCreate(DoctorBase):
    is_active: bool = True
    password: Optional[str] = Field(None, min_length=6)


class DoctorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    specialization: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class DoctorResponse(DoctorBase):
    id: int
    is_active: bool
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PatientSummary(BaseModel):
    id: int
    name: str
    age: int
    phone: str

    model_config = ConfigDict(from_attributes=True)


class DoctorDetailResponse(DoctorResponse):
    patients: List[PatientSummary] = []

    model_config = ConfigDict(from_attributes=True)
