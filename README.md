# Accounts Payable Automation with OCR

A full-stack Accounts Payable Automation application developed as part of the recruitment assignment for **Templegate Technologies & Services Pvt. Ltd.**

The application helps manage invoice processing, OCR-based data extraction, invoice validation, approval workflows, purchase orders, goods receipt notes, three-way matching, payment tracking, and reporting.

## Technology Stack

### Frontend
- React.js
- Vite
- JavaScript
- React Router
- Axios
- Bootstrap
- Recharts

### Backend
- Python
- Django
- Django REST Framework
- Django REST Framework Simple JWT

### Database
- PostgreSQL

### OCR and Document Processing
- Tesseract OCR
- PyMuPDF
- pytesseract
- Pillow

## Features Implemented

### 1. Authentication and Role-Based Access Control
- JWT-based authentication.
- Admin and other role-based permission support.
- Protected API endpoints.
- User authentication and authorization.

### 2. Invoice Management
- Upload invoices in PDF, JPG, JPEG, and PNG formats.
- Extract invoice information using OCR.
- Support multi-page PDF processing.
- Validate mandatory invoice fields.
- Check for duplicate invoices.
- Track invoice status.

### 3. Invoice Approval
- Approve or reject invoices.
- Maintain approval history.
- Track approval status.

### 4. Vendor Management
- Create, view, update, and manage vendor records.

### 5. Purchase Order Management
- Create and manage purchase orders.
- Maintain purchase order line items.

### 6. Goods Receipt Note (GRN)
- Create and manage goods receipt records.
- Track received goods against purchase orders.

### 7. Three-Way Matching
- Compare invoice details with purchase orders and goods receipt notes.
- Identify matching and mismatching records.
- Track matching status.

### 8. Payment Management
- Record invoice payments.
- Track payment status.
- Update invoice status when payment is completed.

### 9. Dashboard and Reports
- View invoice and payment summaries.
- Access vendor and purchase order information.
- View reporting information.

### 10. Audit Logs and Settings
- View recorded audit activities.
- Manage application preferences.

## Demo Login Credentials

Use the following credentials to access the application:

| Field | Details |
|---|---|
| Role | Admin |
| Username | admin |
| Password | admin@123 |

**Note:** The Admin account is provided for project evaluation. Other demo login accounts are not currently provided.

Use a temporary evaluation password. Do not publish a password belonging to a production or company account.

## Project Structure

```text
accounts-payable-automation/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Django application files
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   └── .env.example
│
├── docs/
│   ├── DATABASE_DESIGN.md
│   └── IMPLEMENTATION_PLAN.md
│
├── database_schema.sql
├── .gitignore
└── README.md
```

## Installation and Setup

### Prerequisites

Install the following software:

- Python 3
- Node.js and npm
- PostgreSQL
- Git
- Tesseract OCR

### 1. Clone the Repository

```bash
git clone https://github.com/Sweta8904/accounts-payable-automation.git
cd accounts-payable-automation
```

### 2. Backend Setup

Open PowerShell:

```powershell
cd backend

py -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create the environment configuration file:

```powershell
Copy-Item .env.example .env
```

Update the `.env` file with your local PostgreSQL database configuration.

Do not upload the actual `.env` file to GitHub.

### 3. PostgreSQL Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE ap_automation;
```

Configure the database name, username, password, host, and port in the backend `.env` file.

Run migrations:

```powershell
python manage.py migrate
```

### 4. Create an Admin Account

To create a Django superuser:

```powershell
python manage.py createsuperuser
```

Follow the prompts to enter the username, email, and password.

If the evaluation Admin account has already been created, use its existing credentials instead.

### 5. Start the Django Backend

```powershell
python manage.py runserver
```

Backend URL:

```text
http://127.0.0.1:8000/
```

### 6. Frontend Setup

Open another terminal:

```powershell
cd frontend

npm install
```

Create the frontend environment configuration file:

```powershell
Copy-Item .env.example .env
```

Configure the backend API URL if required by the frontend.

Start the React development server:

```powershell
npm run dev
```

The frontend will be available at the local URL displayed in the terminal, usually:

```text
http://localhost:5173/
```

## Tesseract OCR Configuration

Tesseract OCR must be installed separately on the system.

For Windows, the executable is commonly located at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Configure the Tesseract executable path in the Django OCR settings if necessary.

The application uses PyMuPDF and Tesseract OCR for document text extraction and rule-based field identification.

OCR-extracted information should be reviewed before approval.

## API Overview

| Module | API Endpoint |
|---|---|
| Health Check | `/api/health/` |
| Login | `/api/auth/token/` |
| Refresh Token | `/api/auth/token/refresh/` |
| Current User | `/api/auth/me/` |
| User Management | `/api/auth/users/` |
| Invoices | `/api/invoices/` |
| Invoice Dashboard | `/api/invoices/dashboard/` |
| Invoice Approval | `/api/invoices/<id>/approval/` |
| Vendors | `/api/vendors/` |
| Purchase Orders | `/api/purchase-orders/` |
| Goods Receipt Notes | `/api/grns/` |
| Three-Way Matching | `/api/invoices/<id>/match/` |
| Payments | `/api/payments/` |
| Reports | `/api/reports/summary/` |
| Audit Logs | `/api/audit-logs/` |

## Database Schema

The application uses PostgreSQL.

The database schema export is available in:

```text
database_schema.sql
```

It contains the database structure, including table definitions and relationships.

Additional database documentation is available in:

```text
docs/DATABASE_DESIGN.md
```

## Testing and Verification

The following workflows were tested during development:

- JWT authentication.
- Role-based access restrictions.
- Invoice upload and OCR processing.
- Invoice validation and duplicate checks.
- Invoice approval and rejection.
- Vendor and purchase order management.
- Goods receipt note management.
- Invoice, purchase order, and GRN matching.
- Payment recording and invoice status updates.
- Dashboard and reporting endpoints.

## Current Scope and Limitations

This project demonstrates the core Accounts Payable workflow. Some advanced enterprise features are outside the current implementation:

- No direct banking or payment gateway integration. Payments are manually recorded.
- No automated email invoice ingestion or bulk invoice upload.
- OCR uses text extraction and rule-based field identification, so manual verification may be required.
- No external GST verification integration.
- No configurable multi-level or parallel approval workflow.
- No automated approval reminders or escalation system.
- Audit logging currently covers selected application activities rather than every system action.
- Advanced AP aging and detailed tax analytics are not fully implemented.

## Challenges and Solutions

A separate document describing the main development challenges, solutions, and implementation decisions is included with the project submission.

## Author

**Sweta**

Project: Accounts Payable Automation with OCR

Developed using React.js, Django REST Framework, and PostgreSQL.

**GitHub Repository:**  
https://github.com/Sweta8904/accounts-payable-automation
