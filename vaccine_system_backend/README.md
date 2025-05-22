
# Vaccine Appointment System API

This is a FastAPI backend implementing a vaccine appointment system with:

- User signup/login with hashed passwords
- JWT token authentication
- Role-based access (admin/user)
- CRUD vaccines (admin only)
- Register patients
- Book vaccine appointments
- Record vaccination status

## Setup

1. Create virtual environment (recommended):

```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the app:

```
uvicorn main:app --reload
```

4. Visit the interactive docs at http://127.0.0.1:8000/docs

## Notes

- Uses SQLite by default (test.db file)
- Change DATABASE_URL in main.py for PostgreSQL or other DBs
- Admin role required for vaccine creation and vaccination recording

