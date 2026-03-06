"""
backend/routes/jobs.py
──────────────────────
REST API endpoints for background job management:

  POST /api/jobs/export-csv          — patient triggers their own CSV export
  GET  /api/jobs/export-csv/download — patient downloads the ready CSV
  GET  /api/jobs/task-status/<id>    — poll Celery task status
  POST /api/jobs/test-ping           — admin: verify Celery is running
  POST /api/jobs/trigger-reminders   — admin: manually fire daily reminders
  POST /api/jobs/trigger-reports     — admin: manually fire monthly reports
"""

from flask import Blueprint, request, jsonify, send_file, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Patient
from functools import wraps
import io

jobs_bp = Blueprint('jobs', __name__)


# ─── Role guards ──────────────────────────────────────────────────────────────

def patient_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user = User.query.get(int(get_jwt_identity()))
        if not user or user.role != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user = User.query.get(int(get_jwt_identity()))
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ─── Patient: trigger CSV export ─────────────────────────────────────────────

@jobs_bp.route('/export-csv', methods=['POST'])
@patient_required
def trigger_csv_export():
    """Queue an async CSV export job for the logged-in patient."""
    from ..tasks import task_export_patient_csv
    user = User.query.get(int(get_jwt_identity()))
    patient = user.patient
    if not patient:
        return jsonify({'error': 'Patient profile not found'}), 404

    task = task_export_patient_csv.apply_async(args=[patient.id])
    return jsonify({
        'message': 'Export started. You will receive an email when ready.',
        'task_id': task.id
    }), 202


@jobs_bp.route('/export-csv/download', methods=['GET'])
@patient_required
def download_csv():
    """Download the CSV that was stored in Redis after export."""
    import redis as redis_lib
    from flask import current_app

    user = User.query.get(int(get_jwt_identity()))
    patient = user.patient
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    redis_url = current_app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    r = redis_lib.from_url(redis_url)
    redis_key = f"csv_export:{patient.id}"
    data = r.get(redis_key)

    if not data:
        return jsonify({'error': 'No export found. Please trigger a new export.'}), 404

    return Response(
        data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=treatment_history_{patient.full_name}.csv'}
    )


# ─── Poll task status ────────────────────────────────────────────────────────

@jobs_bp.route('/task-status/<task_id>', methods=['GET'])
@jwt_required()
def task_status(task_id):
    """Poll a Celery task by its ID."""
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    response = {'task_id': task_id, 'status': result.status}
    if result.ready():
        if result.successful():
            response['result'] = result.result
        else:
            response['error'] = str(result.result)
    return jsonify(response)


# ─── Admin: manual triggers ───────────────────────────────────────────────────

@jobs_bp.route('/test-ping', methods=['POST'])
@admin_required
def test_ping():
    """Fire the test ping task — verifies Celery worker is live."""
    from ..tasks import task_test_ping
    task = task_test_ping.apply_async()
    return jsonify({'task_id': task.id, 'message': 'Ping sent to Celery worker'}), 202


@jobs_bp.route('/trigger-reminders', methods=['POST'])
@admin_required
def trigger_reminders():
    """Manually fire the daily reminders task (for testing)."""
    from ..tasks import task_send_daily_reminders
    task = task_send_daily_reminders.apply_async()
    return jsonify({'task_id': task.id, 'message': 'Daily reminders task queued'}), 202


@jobs_bp.route('/trigger-reports', methods=['POST'])
@admin_required
def trigger_reports():
    """Manually fire the monthly reports task (for testing)."""
    from ..tasks import task_send_monthly_reports
    task = task_send_monthly_reports.apply_async()
    return jsonify({'task_id': task.id, 'message': 'Monthly reports task queued'}), 202
