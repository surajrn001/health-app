from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    TokenPayload,
)
from app.schemas.doctor import (
    DoctorBase,
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorDetailResponse,
    PatientSummary,
)
from app.schemas.patient import (
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientDetailResponse,
    DoctorSummary,
)
from app.schemas.assignment import DoctorPatientAssignmentResponse
from app.schemas.common import MessageResponse, PaginationMeta, PaginatedResponse

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenPayload",
    "DoctorBase",
    "DoctorCreate",
    "DoctorUpdate",
    "DoctorResponse",
    "DoctorDetailResponse",
    "PatientSummary",
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "PatientDetailResponse",
    "DoctorSummary",
    "DoctorPatientAssignmentResponse",
    "MessageResponse",
    "PaginationMeta",
    "PaginatedResponse",
]
