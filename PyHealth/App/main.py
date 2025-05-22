from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="PyHealth Ticket & Vaccine System")


# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/vaccines", response_model=list[schemas.VaccineOut])
def list_vaccines(db: Session = Depends(get_db)):
    return crud.get_vaccines(db)


@app.post("/vaccines", response_model=schemas.VaccineOut)
def create_vaccine(vaccine: schemas.VaccineCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_active_admin)):
    return crud.create_vaccine(db, vaccine)


@app.post("/appointments", response_model=schemas.AppointmentOut)
def book_appointment(appointment: schemas.AppointmentCreate,
                     db: Session = Depends(get_db),
                     current_user: models.User = Depends(auth.get_current_active_patient)):
    return crud.create_appointment(db, appointment, current_user)


@app.get("/tickets", response_model=list[schemas.TicketOut])
def list_tickets(db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_tickets_for_user(db, current_user)


@app.post("/tickets", response_model=schemas.TicketOut)
def create_ticket(ticket: schemas.TicketCreate,
                  db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.create_ticket(db, ticket, current_user)
