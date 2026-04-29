# TempoCode

A minimalist coding practice platform focused on programming fluency, program structure, and software modeling.

## Stack

| Layer    | Tech              |
|----------|-------------------|
| Frontend | React + Vite      |
| Backend  | Python + FastAPI  |
| Database | PostgreSQL        |

## Project Structure

```
TempoCode/
├── frontend/       # React + Vite app
├── backend/        # FastAPI app
│   └── app/
│       ├── main.py
│       ├── models/     # SQLAlchemy ORM models
│       ├── routes/     # API route handlers
│       ├── schemas/    # Pydantic request/response schemas
│       ├── services/   # Grading logic
│       └── db/         # DB connection + session
├── database/
│   └── schema.sql  # Run this to initialize the DB
└── .gitignore
```

## Setup

### Database

1. Make sure PostgreSQL is running on `localhost:5432`
2. Create the database:
   ```bash
   psql -U postgres -c "CREATE DATABASE tempocode;"
   ```
3. Run the schema:
   ```bash
   psql -U postgres -d tempocode -f database/schema.sql
   ```

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # then fill in your DB password
uvicorn app.main:app --reload
```

API runs at: `http://localhost:8000`  
Docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at: `http://localhost:5173`

## Practice Modes

| Mode | Description |
|------|-------------|
| Flow + Implementation | Arrange flow steps → green → write code → green |
| Debugging | Fix broken Python code with syntax and semantic errors |
| Mock Interview | Describe what a code block does — AI evaluates |
