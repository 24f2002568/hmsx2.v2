"""
backend/tasks.py
────────────────
All Celery background tasks for MEDIX HMS:

  1. task_send_daily_reminders   – scheduled 08:00 daily
  2. task_send_monthly_reports   – scheduled 1st of every month 06:00
  3. task_export_patient_csv     – user-triggered async CSV export
  4. task_test_ping              – admin test task

Run workers:
    celery -A celery_worker.celery worker --loglevel=info
    celery -A celery_worker.celery beat   --loglevel=info
"""

from . import celery
from datetime import date, datetime
import csv, io, logging, requests

log = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _send_mail(subject, html_body, recipients):
    from . import mail
    from flask_mail import Message
    try:
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        mail.send(msg)
        log.info("Mail sent to %s — %s", recipients, subject)
    except Exception as exc:
        log.warning("Mail not sent (%s): %s", subject, exc)


def _gchat(text):
    from flask import current_app
    url = current_app.config.get('GCHAT_WEBHOOK_URL', '')
    if not url:
        log.info("[GChat skipped] %s", text)
        return
    try:
        requests.post(url, json={"text": text}, timeout=5)
    except Exception as exc:
        log.warning("GChat error: %s", exc)


# ─── Task 1: Daily Reminders ──────────────────────────────────────────────────

@celery.task(name='backend.tasks.task_send_daily_reminders', bind=True)
def task_send_daily_reminders(self):
    """
    Scheduled: 08:00 every day via Celery Beat.
    Sends appointment reminder emails + Google Chat messages for all
    appointments today with status=Booked.
    """
    from .models import Appointment
    today = date.today()
    appointments = Appointment.query.filter_by(date=today, status='Booked').all()

    sent = 0
    for appt in appointments:
        patient  = appt.patient
        doctor   = appt.doctor
        email    = patient.user.email if patient.user else None
        name     = patient.full_name
        doc_name = f"Dr. {doctor.full_name}"
        time_str = appt.time

        if email:
            html = _reminder_email_html(name, doc_name, today.strftime('%d %B %Y'), time_str)
            _send_mail(
                subject=f"[MEDIX] Appointment Reminder — Today at {time_str}",
                html_body=html,
                recipients=[email]
            )

        _gchat(
            f"*MEDIX Reminder* | {name} has an appointment with {doc_name} "
            f"today ({today.strftime('%d %b %Y')}) at *{time_str}*."
        )

        log.info("Reminder sent → %s (%s) at %s", name, email, time_str)
        sent += 1

    return {"sent": sent, "date": today.isoformat()}


def _reminder_email_html(patient_name, doctor_name, date_str, time_str):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{font-family:'Helvetica Neue',sans-serif;background:#f5f5f3;margin:0;padding:40px 20px;}}
.card{{background:#fff;max-width:520px;margin:0 auto;border-radius:4px;border:1px solid #e0e0e0;overflow:hidden;}}
.header{{background:#0a0a0a;padding:28px 32px;}}
.header h1{{color:#fff;font-size:22px;font-weight:800;letter-spacing:0.1em;margin:0;}}
.header p{{color:#666;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;margin:4px 0 0;}}
.body{{padding:32px;}}
.body p{{color:#3a3a3a;font-size:15px;line-height:1.7;margin:0 0 16px;}}
.box{{background:#f5f5f3;border:1px solid #e0e0e0;border-left:3px solid #0a0a0a;border-radius:2px;padding:16px 20px;margin:20px 0;}}
.row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #ebebeb;font-size:13px;}}
.row:last-child{{border-bottom:none;}}
.lbl{{color:#6a6a6a;font-family:monospace;letter-spacing:0.08em;}}
.val{{font-weight:700;color:#0a0a0a;}}
.footer{{background:#f5f5f3;border-top:1px solid #e0e0e0;padding:16px 32px;font-size:11px;color:#6a6a6a;font-family:monospace;}}
</style></head><body>
<div class="card">
  <div class="header"><h1>MEDIX</h1><p>Hospital Management System</p></div>
  <div class="body">
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>This is a reminder that you have a scheduled appointment <strong>today</strong>. Please arrive 15 minutes early.</p>
    <div class="box">
      <div class="row"><span class="lbl">DOCTOR</span><span class="val">{doctor_name}</span></div>
      <div class="row"><span class="lbl">DATE</span><span class="val">{date_str}</span></div>
      <div class="row"><span class="lbl">TIME</span><span class="val">{time_str}</span></div>
    </div>
    <p style="font-size:13px;color:#6a6a6a;">To cancel or reschedule, log in to MEDIX before your appointment time.</p>
  </div>
  <div class="footer">MEDIX HMS &nbsp;|&nbsp; Automated reminder</div>
</div></body></html>"""


# ─── Task 2: Monthly Activity Report ─────────────────────────────────────────

@celery.task(name='backend.tasks.task_send_monthly_reports', bind=True)
def task_send_monthly_reports(self):
    """
    Scheduled: 06:00 on the 1st of every month via Celery Beat.
    Generates an HTML report for the previous month for each doctor and emails it.
    """
    from .models import Doctor, Appointment
    from sqlalchemy import extract
    from calendar import month_name

    today = date.today()
    if today.month == 1:
        report_month, report_year = 12, today.year - 1
    else:
        report_month, report_year = today.month - 1, today.year

    doctors = Doctor.query.all()
    reports_sent = 0

    for doctor in doctors:
        email = doctor.user.email if doctor.user else None
        if not email:
            continue

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == 'Completed',
            extract('year',  Appointment.date) == report_year,
            extract('month', Appointment.date) == report_month,
        ).order_by(Appointment.date).all()

        html = _monthly_report_html(
            doctor_name=doctor.full_name,
            specialization=doctor.specialization or '',
            month_label=f"{month_name[report_month]} {report_year}",
            appointments=appointments
        )

        _send_mail(
            subject=f"[MEDIX] Monthly Report — {month_name[report_month]} {report_year}",
            html_body=html,
            recipients=[email]
        )

        log.info("Monthly report → Dr. %s (%d appts)", doctor.full_name, len(appointments))
        reports_sent += 1

    return {"reports_sent": reports_sent, "month": report_month, "year": report_year}


def _monthly_report_html(doctor_name, specialization, month_label, appointments):
    rows = ""
    for i, a in enumerate(appointments, 1):
        t = a.treatment
        rows += f"""<tr>
          <td>{i}</td><td>{a.date}</td><td>{a.time}</td>
          <td>{a.patient.full_name if a.patient else '—'}</td>
          <td>{t.diagnosis if t else '—'}</td>
          <td>{t.prescription if t else '—'}</td>
          <td>{str(t.next_visit) if (t and t.next_visit) else '—'}</td>
        </tr>"""
    if not rows:
        rows = '<tr><td colspan="7" style="text-align:center;color:#6a6a6a;padding:20px;">No completed appointments this month.</td></tr>'

    unique_patients = len(set(a.patient_id for a in appointments))
    prescriptions   = sum(1 for a in appointments if a.treatment and a.treatment.prescription)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{font-family:'Helvetica Neue',sans-serif;background:#f5f5f3;margin:0;padding:40px 20px;}}
.card{{background:#fff;max-width:820px;margin:0 auto;border-radius:4px;border:1px solid #e0e0e0;}}
.header{{background:#0a0a0a;padding:28px 32px;display:flex;justify-content:space-between;align-items:flex-end;}}
.header h1{{color:#fff;font-size:22px;font-weight:800;letter-spacing:0.1em;margin:0;}}
.meta{{color:#888;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;text-align:right;}}
.meta strong{{color:#ccc;display:block;font-size:13px;margin-bottom:2px;}}
.body{{padding:32px;}}
.summary{{display:flex;gap:16px;margin-bottom:28px;}}
.stat{{flex:1;background:#f5f5f3;border:1px solid #e0e0e0;border-left:3px solid #0a0a0a;padding:14px 16px;border-radius:2px;}}
.stat .num{{font-size:28px;font-weight:800;color:#0a0a0a;}}
.stat .lbl{{font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:#6a6a6a;font-family:monospace;margin-top:3px;}}
table{{width:100%;border-collapse:collapse;font-size:12px;}}
th{{font-family:monospace;font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#6a6a6a;
    padding:10px 12px;border-bottom:2px solid #e0e0e0;text-align:left;}}
td{{padding:11px 12px;border-bottom:1px solid #ebebeb;color:#3a3a3a;vertical-align:top;}}
tr:hover td{{background:#f5f5f3;}}
.footer{{background:#f5f5f3;border-top:1px solid #e0e0e0;padding:14px 32px;font-size:11px;color:#6a6a6a;font-family:monospace;}}
</style></head><body>
<div class="card">
  <div class="header">
    <div><h1>MEDIX</h1><p style="color:#666;font-size:11px;letter-spacing:0.15em;text-transform:uppercase;margin:4px 0 0;">Monthly Activity Report</p></div>
    <div class="meta"><strong>Dr. {doctor_name}</strong>{specialization}<br/>{month_label}</div>
  </div>
  <div class="body">
    <div class="summary">
      <div class="stat"><div class="num">{len(appointments)}</div><div class="lbl">Completed</div></div>
      <div class="stat"><div class="num">{unique_patients}</div><div class="lbl">Unique Patients</div></div>
      <div class="stat"><div class="num">{prescriptions}</div><div class="lbl">Prescriptions</div></div>
    </div>
    <table>
      <thead><tr><th>#</th><th>Date</th><th>Time</th><th>Patient</th><th>Diagnosis</th><th>Prescription</th><th>Next Visit</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <div class="footer">MEDIX HMS &nbsp;|&nbsp; Generated {date.today()}</div>
</div></body></html>"""


# ─── Task 3: Patient CSV Export (user-triggered async) ────────────────────────

@celery.task(name='backend.tasks.task_export_patient_csv', bind=True)
def task_export_patient_csv(self, patient_id: int):
    """
    Triggered by the patient clicking 'Export CSV' on the dashboard.
    Stores the result in Redis for 1 hour, then emails the patient.
    """
    import redis as redis_lib
    from flask import current_app
    from .models import Patient, Appointment

    patient = Patient.query.get(patient_id)
    if not patient:
        return {"error": "Patient not found"}

    appointments = Appointment.query.filter_by(patient_id=patient.id)\
        .order_by(Appointment.date.desc()).all()

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Appointment ID', 'Date', 'Time', 'Doctor', 'Specialization',
        'Status', 'Reason', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'
    ])
    for a in appointments:
        t = a.treatment
        writer.writerow([
            a.id, a.date, a.time,
            a.doctor.full_name if a.doctor else '',
            a.doctor.specialization if a.doctor else '',
            a.status, a.reason or '',
            t.diagnosis    if t else '',
            t.prescription if t else '',
            t.notes        if t else '',
            str(t.next_visit) if (t and t.next_visit) else '',
        ])

    csv_data = output.getvalue()

    # Store in Redis for 1 hour (3600 seconds)
    redis_url = current_app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    r = redis_lib.from_url(redis_url)
    redis_key = f"csv_export:{patient_id}"
    r.setex(redis_key, 3600, csv_data.encode('utf-8'))

    # Email notification
    email = patient.user.email if patient.user else None
    if email:
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="font-family:sans-serif;background:#f5f5f3;margin:0;padding:40px 20px;">
<div style="background:#fff;max-width:520px;margin:0 auto;border-radius:4px;border:1px solid #e0e0e0;overflow:hidden;">
  <div style="background:#0a0a0a;padding:24px 28px;"><h1 style="color:#fff;font-size:20px;font-weight:800;letter-spacing:0.1em;margin:0;">MEDIX</h1></div>
  <div style="padding:28px;">
    <p style="font-size:15px;color:#3a3a3a;">Hi <strong>{patient.full_name}</strong>,</p>
    <p style="font-size:14px;color:#3a3a3a;line-height:1.7;">
      Your treatment history CSV export is ready with <strong>{len(appointments)} records</strong>.
      Log in to MEDIX → Appointments → Download CSV to get your file.
    </p>
    <p style="font-size:12px;color:#6a6a6a;">This export will be available for 1 hour.</p>
  </div>
  <div style="background:#f5f5f3;border-top:1px solid #e0e0e0;padding:14px 28px;font-size:11px;color:#6a6a6a;font-family:monospace;">
    MEDIX HMS &nbsp;|&nbsp; Automated notification
  </div>
</div></body></html>"""
        _send_mail("[MEDIX] Your CSV Export is Ready", html, [email])

    log.info("CSV export ready for patient %d — %d records", patient_id, len(appointments))
    return {"patient_id": patient_id, "records": len(appointments), "redis_key": redis_key}


# ─── Task 4: Test ping ────────────────────────────────────────────────────────

@celery.task(name='backend.tasks.task_test_ping', bind=True)
def task_test_ping(self):
    """Admin tool to confirm Celery worker is alive."""
    return {
        "status": "pong",
        "worker": self.request.hostname,
        "time": str(datetime.utcnow())
    }
