python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip freeze > requirements.txt

uvicorn app.main:app --reload --port 8000
