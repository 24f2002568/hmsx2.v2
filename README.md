# MEDIX — Hospital Management System V2

A full-stack Hospital Management System built with **Flask** (backend), **Vue.js** (frontend), **Redis** (caching + message broker), and **Celery** (background jobs).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, Flask-Caching |
| Frontend | Vue.js 3, Vue Router 4, Pinia, Vite |
| Database | SQLite |
| Cache | Redis + Flask-Caching |
| Task Queue | Celery + Redis Broker |
| Email | Flask-Mail (SMTP) |
| Notifications | Google Chat Webhooks |
| UI Framework | Bootstrap 5 |
| Task Monitor | Flower |

## Quick Start (One Command)

```bash
chmod +x start_dev.sh
./start_dev.sh
```

Then in a second terminal:
```bash
cd frontend && npm install && npm run dev
```

## Manual Setup

### 1. Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your SMTP credentials, Redis URL, etc.
```

### 3. Initialise Database + Seed Admin
```bash
python run.py
# Creates DB, seeds departments, creates admin user
# Admin: username=admin | password=admin@123
```

### 4. Start Redis (required for Celery and Caching)
```bash
# macOS
brew install redis && brew services start redis

# Ubuntu / Debian
sudo apt install redis-server && sudo systemctl start redis

# Verify
redis-cli ping   # should return PONG
```

### 5. Start Celery Worker (background task processor)
```bash
celery -A celery_worker.celery worker --loglevel=info
```

### 6. Start Celery Beat (scheduled task runner)
```bash
celery -A celery_worker.celery beat --loglevel=info
```

### 7. (Optional) Flower — Visual task monitor
```bash
celery -A celery_worker.celery flower
# Open http://localhost:5555
```

### 8. Start Flask API
```bash
python run.py
# Runs on http://localhost:5000
```

### 9. Start Vue Dev Server
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

## Background Jobs

### Scheduled Jobs (Celery Beat)

| Job | Schedule | Description |
|-----|----------|-------------|
| Daily Reminders | 08:00 every day | Emails + Google Chat for today's appointments |
| Monthly Reports | 1st of month 06:00 | HTML activity report emailed to each doctor |

### User-Triggered Jobs

| Job | Trigger | Description |
|-----|---------|-------------|
| CSV Export | Patient clicks "Generate Export" | Async treatment history export; email notification on completion |

### Manual Test Triggers (Admin Panel)
Navigate to **Admin → Background Jobs** to:
- Ping the Celery worker (confirm it's alive)
- Manually fire daily reminders
- Manually fire monthly reports
- Track task status in real-time

## Redis Caching

| Endpoint | Cache Key | TTL |
|----------|-----------|-----|
| GET /api/departments/ | `all_departments` | 10 min |
| GET /api/patient/doctors | `all_active_doctors` | 5 min |
| GET /api/admin/dashboard | `admin_dashboard_stats` | 2 min |

Cache is automatically invalidated when data changes (e.g., doctor added → `all_active_doctors` cleared).

## Email Configuration (.env)

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password   # Gmail App Password (not login password)
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Gmail App Password**: Google Account → Security → 2-Step Verification → App Passwords

## Google Chat Webhook (.env)

```env
GCHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/XXX/messages?key=YYY&token=ZZZ
```

Get webhook: Google Chat Space → Manage webhooks → Add webhook

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin@123` |
| Doctor | Set by admin | `doctor@123` (default) |
| Patient | Self-register | User-defined |

## Project Structure

```
hms/
├── backend/
│   ├── __init__.py       Flask app factory + Celery init + Redis cache
│   ├── models.py         SQLAlchemy models
│   ├── tasks.py          Celery tasks (reminders, reports, CSV export)
│   └── routes/
│       ├── auth.py       Login/Register
│       ├── admin.py      Admin APIs (with Redis caching)
│       ├── doctor.py     Doctor APIs
│       ├── patient.py    Patient APIs (with Redis caching)
│       ├── departments.py (with Redis caching + cache invalidation)
│       └── jobs.py       Background job trigger/status endpoints
├── frontend/src/views/
│   ├── admin/AdminJobs.vue    Job dashboard, ping, manual triggers
│   └── patient/PatientExport.vue  CSV export with real-time status
├── celery_worker.py      Celery entrypoint
├── start_dev.sh          One-command dev launcher
└── requirements.txt
```


## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS |
| Frontend | Vue.js 3, Vue Router 4, Pinia, Vite |
| Database | SQLite |
| Cache | Redis |
| Task Queue | Celery + Redis |
| UI Framework | Bootstrap 5 |
| Styling | Custom CSS (Black & White design system) |

## Project Structure

```
hms/
├── backend/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── tasks.py             # Celery tasks
│   └── routes/
│       ├── auth.py          # Login, Register
│       ├── admin.py         # Admin APIs
│       ├── doctor.py        # Doctor APIs
│       ├── patient.py       # Patient APIs
│       ├── appointments.py
│       └── departments.py
├── frontend/
│   ├── src/
│   │   ├── views/           # Vue pages (Admin/Doctor/Patient)
│   │   ├── store/auth.js    # Pinia store + Axios
│   │   ├── router/index.js  # Vue Router with role guards
│   │   └── assets/main.css  # Design system
│   ├── index.html
│   └── vite.config.js
├── run.py                   # App entry point + DB seeder
└── requirements.txt
```

## Setup Instructions

### 1. Clone and Install

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Run Database Setup & Seed Admin

```bash
python run.py
```
This creates the SQLite database, seeds departments, and creates the admin user.

- **Admin**: `username=admin` / `password=admin@123`

### 3. Start Development Servers

**Backend (Flask)**:
```bash
python run.py
# Runs on http://localhost:5000
```

**Frontend (Vue Dev Server)**:
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### 4. Build for Production

```bash
cd frontend
npm run build
# Output goes to backend/static/
# Then just run: python run.py
```

### 5. Start Redis & Celery (for background jobs)

```bash
# Start Redis
redis-server

# Start Celery Worker
celery -A backend.tasks worker --loglevel=info

# Start Celery Beat (scheduled jobs)
celery -A backend.tasks beat --loglevel=info
```

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin@123` |
| Doctor | Set by admin | `doctor@123` (default) |
| Patient | Self-register | User-defined |

## Features

### Admin
- Dashboard with stats (doctors, patients, appointments)
- Add/edit/deactivate doctors
- Search patients by name/phone/email
- View all appointments with status filtering
- Manage departments

### Doctor
- Dashboard with today's/week's schedule
- Mark appointments as completed with treatment notes
- Set availability for next 7 days
- View full patient history

### Patient
- Register and manage profile
- Search doctors by name/specialization
- Book, reschedule, cancel appointments
- View treatment history
- Export treatment history as CSV

## Background Jobs (Celery)

- **Daily Reminders** (8:00 AM): Notifies patients with same-day appointments
- **Monthly Reports** (1st of month): Sends doctor activity summaries
- **CSV Export**: On-demand async export for patients

## Demo Video

[Link to demo video]
