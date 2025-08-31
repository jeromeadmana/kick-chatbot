# Kick Chatbot — Backend (FastAPI)

## Local setup

1. Create & activate virtualenv
```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

2. Install
pip install -r requirements.txt

3. Copy .env.example -> .env and fill secrets (DATABASE_URL, SECRET_KEY, etc.)

4. Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
