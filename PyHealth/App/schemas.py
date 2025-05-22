from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    staff = "staff"
    patient = "patient"


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class VaccineBase(BaseModel):
    name: str
    manufacturer: Optional[str]
    doses_required: Optional[int] = 1
    storage_requirements: Optional[str]


class VaccineCreate(VaccineBase):
    pass


class VaccineOut(VaccineBase):
    id: int

    class Config:
        orm_mode = True


class AppointmentBase(BaseModel):
    vaccine_id: int
    scheduled_date: datetime
    dose_number: Optional[int] = 1


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentOut(AppointmentBase):
    id: int
    patient_id: int
    status: str

    class Config:
        orm_mode = True


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None


class TicketCreate(TicketBase):
    pass


class TicketOut(TicketBase):
    id: int
    status: TicketStatus
    created_at: datetime

    class Config:
        orm_mode = True
