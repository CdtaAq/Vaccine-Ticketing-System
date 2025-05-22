
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session

# --- CONFIG ---

DATABASE_URL = "sqlite:///./test.db"  # Use postgresql://user:pass@localhost/dbname for Postgres

SECRET_KEY = "secretjwtkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base = declarative_base()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app = FastAPI()

# --- DB MODELS ---

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

class VaccineModel(Base):
    __tablename__ = "vaccines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    manufacturer = Column(String)
    doses_required = Column(Integer)
    storage_requirements = Column(String)

class PatientModel(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)

class AppointmentModel(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    vaccine_id = Column(Integer, ForeignKey("vaccines.id"))
    appointment_date = Column(DateTime)
    status = Column(String, default="scheduled")

    patient = relationship("PatientModel")
    vaccine = relationship("VaccineModel")

# --- Pydantic Schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserOut(BaseModel):
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class VaccineBase(BaseModel):
    name: str
    manufacturer: str
    doses_required: int
    storage_requirements: str

class VaccineCreate(VaccineBase):
    pass

class Vaccine(VaccineBase):
    id: int
    class Config:
        orm_mode = True

class PatientBase(BaseModel):
    email: EmailStr
    name: str
    age: int

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    patient_id: int
    vaccine_id: int
    appointment_date: datetime

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    status: str

    class Config:
        orm_mode = True

# --- UTILS ---

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Dependency to get current user
from fastapi import Security

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# --- ROUTES ---

@app.post("/signup", response_model=UserOut, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = get_password_hash(user.password)
    new_user = UserModel(email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/vaccines", response_model=Vaccine)
def create_vaccine(
    vaccine: VaccineCreate,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_current_admin),
):
    new_vaccine = VaccineModel(**vaccine.dict())
    db.add(new_vaccine)
    db.commit()
    db.refresh(new_vaccine)
    return new_vaccine

@app.get("/vaccines", response_model=List[Vaccine])
def list_vaccines(db: Session = Depends(get_db)):
    return db.query(VaccineModel).all()

@app.post("/patients", response_model=Patient)
def register_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # Check duplicate patient email
    if db.query(PatientModel).filter(PatientModel.email == patient.email).first():
        raise HTTPException(status_code=400, detail="Patient already registered")
    new_patient = PatientModel(**patient.dict())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.post("/appointments", response_model=Appointment)
def book_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    patient = db.query(PatientModel).filter(PatientModel.id == appointment.patient_id).first()
    vaccine = db.query(VaccineModel).filter(VaccineModel.id == appointment.vaccine_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    new_appointment = AppointmentModel(**appointment.dict())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@app.get("/appointments", response_model=List[Appointment])
def list_appointments(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    return db.query(AppointmentModel).all()

@app.post("/appointments/{appointment_id}/vaccinate", response_model=Appointment)
def record_vaccination(
    appointment_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_current_admin),
):
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = status_update.get("status", "completed")
    db.commit()
    db.refresh(appointment)
    return appointment

# --- Create tables on startup ---
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
