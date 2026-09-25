# Healthcare Management Backend API

A backend system built with FastAPI, SQLAlchemy, Pydantic, and JWT authentication for managing Doctors and Patients.

---

## Tech Stack
- Python 3.9+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- SQLite / PostgreSQL
- PyJWT & Bcrypt
- Uvicorn
- Alembic
- Pytest

---

## Project Structure

```
Health_app/
├── app/
│   ├── main.py                  # FastAPI application entrypoint
│   ├── config.py                # App configuration via pydantic-settings
│   ├── database.py              # Database engine and session dependency
│   ├── limiter.py               # Rate limiter
│   ├── auth/                    # Authentication and RBAC
│   │   ├── jwt.py               # Password hashing and JWT generation
│   │   └── dependencies.py      # Auth and role dependencies
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py              # User model (admin/doctor)
│   │   ├── doctor.py            # Doctor model
│   │   ├── patient.py           # Patient model
│   │   └── doctor_patient.py    # Doctor-Patient association
│   ├── schemas/                 # Pydantic schemas
│   │   ├── auth.py              # Auth request/response schemas
│   │   ├── doctor.py            # Doctor schemas
│   │   ├── patient.py           # Patient schemas
│   │   ├── assignment.py        # Assignment schemas
│   │   └── common.py            # Pagination schemas
│   ├── crud/                    # Business logic and database operations
│   │   ├── crud_user.py
│   │   ├── crud_doctor.py
│   │   ├── crud_patient.py
│   │   └── crud_assignment.py
│   └── routers/                 # API route handlers
│       ├── auth.py              # /auth endpoints
│       ├── doctors.py           # /doctors endpoints
│       └── patients.py          # /patients endpoints
├── alembic/                     # Database migrations
├── tests/                       # Automated test suite (26 tests)
├── .env.example                 # Environment variables template
├── .env                         # Local environment file
├── Dockerfile                   # Docker build file
├── docker-compose.yml           # Docker compose file
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Project dependencies
├── seed_data.py                 # Sample database seeder
└── README.md
```

---

## Setup Instructions

### 1. Local Environment Setup

Create and activate virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install dependencies:
```powershell
pip install -r requirements.txt
```

Set up environment variables:
```powershell
copy .env.example .env
```

Apply database migrations:
```powershell
alembic upgrade head
```

Seed initial test data (optional):
```powershell
python seed_data.py
```

Run development server:
```powershell
uvicorn app.main:app --reload --port 8000
```

- API Docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

### 2. Docker Setup

To run using Docker:
```bash
docker-compose up --build
```

---

## Environment Configuration

Configuration variables in `.env`:

| Variable | Description | Default |
|---|---|---|
| `PROJECT_NAME` | Name of the API | `Health App API` |
| `SECRET_KEY` | Secret key for JWT signing | `secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration | `120` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./health_app.db` |
| `RATE_LIMIT_DEFAULT` | Default rate limit | `100/minute` |
| `RATE_LIMIT_AUTH` | Auth endpoints rate limit | `20/minute` |

---

## How Authentication Works

1. **Password Hashing:** Passwords are hashed using bcrypt before storing in the database.
2. **Login (`POST /auth/login`):** Users authenticate with email and password. On success, the API returns a JWT access token containing the user ID, email, and role.
3. **Protected Requests:** Clients send the token in the `Authorization` header:
   ```
   Authorization: Bearer <access_token>
   ```
4. **Role Enforcement:**
   - **Admin:** Can create doctors, soft-delete doctors, view all patients, and manage assignments.
   - **Doctor:** Can only view and update their assigned patients. Attempting to view unassigned patients returns `403 Forbidden`.

---

## API Flow Overview

### Authentication
- `POST /auth/register` - Register a new user (`admin` or `doctor`)
- `POST /auth/login` - Authenticate and obtain JWT token
- `GET /auth/me` - Get current user profile

### Doctor Management
- `POST /doctors` - Create doctor (Admin only)
- `GET /doctors` - List doctors (Supports pagination and search)
- `GET /doctors/{doctor_id}` - Get doctor details
- `PUT /doctors/{doctor_id}` - Update doctor (Admin or self)
- `DELETE /doctors/{doctor_id}` - Soft delete doctor (Admin only, sets `is_active=False`)

### Patient Management
- `POST /patients` - Create patient (Validates age > 0, phone 10-15 digits)
- `GET /patients` - List patients (Admin sees all; Doctor sees only assigned patients)
- `GET /patients/{patient_id}` - Get patient details (Admin sees any; Doctor sees only if assigned)
- `PUT /patients/{patient_id}` - Update patient details

### Doctor-Patient Assignment
- `POST /doctors/{doctor_id}/patients/{patient_id}` - Assign patient to doctor
- `GET /doctors/{doctor_id}/patients` - Fetch doctor's assigned patients (Doctor can only access their own list)

---

## Running Unit Tests

Run the test suite with pytest:
```powershell
pytest -v
```

All 26 tests cover authentication, doctor CRUD, patient CRUD, validations, and role-based access restrictions.

---

## Default Test Accounts

After running `python seed_data.py`:

| Role | Email | Password | Details |
|---|---|---|---|
| **Admin** | `admin@healthapp.com` | `AdminPassword123` | Full administrative access |
| **Doctor** | `dr.strange@healthapp.com` | `Doctor@123` | Assigned to John Doe, Jane Smith |
| **Doctor** | `dr.house@healthapp.com` | `Doctor@123` | Assigned to Robert Brown, Emily Davis |

---

## Assumptions & Design Decisions

1. **Doctor Accounts:** When an Admin creates a Doctor, an associated login user account is created with role `doctor` so they can log into the system.
2. **Soft Deletion:** Deleting a doctor sets `is_active = False` on the doctor and their user account, preventing new assignments or logins while preserving history.
3. **Doctor Privacy:** Doctors can only see patients assigned to them via the `doctor_patient` table. Accessing unassigned patients returns `403 Forbidden`.
4. **Auto-Assignment:** When a doctor creates a patient via `POST /patients`, the patient is automatically assigned to that doctor.
5. **Phone Format:** Cleaned and verified to have between 10 and 15 digits (optional leading `+`).
