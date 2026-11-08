# Accounts Payable Automation

Initial full-stack scaffold for the Templegate Technologies & Services recruitment assignment.

## Stack
- React + Vite, JavaScript, React Router, Axios, Bootstrap, Recharts
- Django + Django REST Framework
- PostgreSQL
- JWT (Simple JWT)
- Tesseract OCR + PyMuPDF (OCR service will be implemented in the invoice-processing phase)

## Start here
See `docs/IMPLEMENTATION_PLAN.md` and `docs/DATABASE_DESIGN.md`.

### Backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
Configure PostgreSQL values in `.env`, then:
```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

The scaffold is the starting point, not a claim that all required modules are already complete. Build and verify each module incrementally.
