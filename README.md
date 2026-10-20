# CampusCare — College Grievance Redressal System

## Features
- Submit grievances and receive a generated ID such as GRV00001.
- Track a grievance by ID.
- Look up complaints using the email entered during submission.
- Admin dashboard to filter grievances, update status, and add remarks.
- SQLite database stores complaints between app restarts.
- Responsive web design.

## Run on Windows 11 in VS Code
Open this folder in VS Code. Choose Terminal → New Terminal, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use Command Prompt and run:
```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Demo admin login
Username: `admin`
Password: `Admin@123`

## Important
This is a classroom starter, not production-ready. The email lookup is not authentication, and tracking by ID is not sufficient access control for sensitive complaints. Before real deployment, add student accounts, role-based authorization, CSRF protection, secure secret management, rate limiting, audit/status history, backups, and disable Flask debug mode. Use test data only in this demo.
