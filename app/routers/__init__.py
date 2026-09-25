from app.routers.auth import router as auth_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router

__all__ = ["auth_router", "doctors_router", "patients_router"]
