# ARCDIS Backend

ARCDIS (Attack Detection & Prevention System) FastAPI backend.

## Requirements
- Python 3.11+
- MongoDB 

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
cd 
```

3. Configure environment:
Copy `.env.example` to `.env` and adjust the variables (especially MongoDB URL and JWT secret).
```bash
cp .env.example .env
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation
Once running, access the interactive API docs at `http://127.0.0.1:8000/docs`.
