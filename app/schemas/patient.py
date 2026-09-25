import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class DoctorSummary(BaseModel):
    id: int
    name: str
    specialization: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class PatientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    age: int = Field(..., gt=0, le=130)
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v.strip())
        if not re.match(r"^\+?[0-9]{10,15}$", cleaned):
            raise ValueError("Phone number must contain between 10 and 15 digits")
        return cleaned


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    age: Optional[int] = Field(None, gt=0, le=130)
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\(\)]", "", v.strip())
        if not re.match(r"^\+?[0-9]{10,15}$", cleaned):
            raise ValueError("Phone number must contain between 10 and 15 digits")
        return cleaned


class PatientResponse(PatientBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PatientDetailResponse(PatientResponse):
    doctors: List[DoctorSummary] = []

    model_config = ConfigDict(from_attributes=True)
