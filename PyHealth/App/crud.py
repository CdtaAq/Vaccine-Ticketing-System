from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_vaccines(db: Session):
    return db.query(models.Vaccine).all()


def create_vaccine(db: Session, vaccine: schemas.VaccineCreate):
    db_vaccine = models.Vaccine(**vaccine.dict())
    db.add(db_vaccine)
    db.commit()
    db.refresh(db_vaccine)
    return db_vaccine


def create_appointment(db: Session, appointment: schemas.AppointmentCreate, patient: models.User):
    db_appointment = models.Appointment(
        patient_id=patient.id,
        vaccine_id=appointment.vaccine_id,
        scheduled_date=appointment.scheduled_date,
        dose_number=appointment.dose_number,
        status="scheduled"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def get_tickets_for_user(db: Session, user: models.User):
    if user.role == models.UserRole.admin:
        return db.query(models.Ticket).all()
    else:
        return db.query(models.Ticket).filter(models.Ticket.created_by == user.id).all()


def create_ticket(db: Session, ticket: schemas.TicketCreate, user: models.User):
    db_ticket = models.Ticket(
        created_by=user.id,
        title=ticket.title,
        description=ticket.description,
        status=models.TicketStatus.open,
        created_at=datetime.utcnow()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
