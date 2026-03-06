from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Doctor, Appointment, Treatment, DoctorAvailability, db
from datetime import datetime, date, timedelta
from functools import wraps

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        return f(*args, **kwargs)
    return decorated

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    doctor = user.doctor
    today = date.today()
    week_end = today + timedelta(days=7)

    today_appts = Appointment.query.filter_by(doctor_id=doctor.id, date=today, status='Booked').count()
    week_appts = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= today,
        Appointment.date <= week_end,
        Appointment.status == 'Booked'
    ).count()
    total_patients = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct().count()

    return jsonify({
        'doctor': doctor.to_dict(),
        'today_appointments': today_appts,
        'week_appointments': week_appts,
        'total_patients': total_patients
    })

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    filter_type = request.args.get('filter', 'upcoming')
    today = date.today()

    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if filter_type == 'today':
        query = query.filter_by(date=today, status='Booked')
    elif filter_type == 'upcoming':
        query = query.filter(Appointment.date >= today, Appointment.status == 'Booked')
    elif filter_type == 'past':
        query = query.filter(Appointment.date < today)

    appointments = query.order_by(Appointment.date, Appointment.time).all()
    return jsonify([a.to_dict() for a in appointments])

@doctor_bp.route('/appointments/<int:appt_id>/complete', methods=['POST'])
@doctor_required
def complete_appointment(appt_id):
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()
    data = request.get_json()

    appt.status = 'Completed'
    if not appt.treatment:
        treatment = Treatment(
            appointment_id=appt.id,
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            notes=data.get('notes', ''),
        )
        next_visit = data.get('next_visit')
        if next_visit:
            treatment.next_visit = datetime.strptime(next_visit, '%Y-%m-%d').date()
        db.session.add(treatment)
    else:
        appt.treatment.diagnosis = data.get('diagnosis', appt.treatment.diagnosis)
        appt.treatment.prescription = data.get('prescription', appt.treatment.prescription)
        appt.treatment.notes = data.get('notes', appt.treatment.notes)

    db.session.commit()
    return jsonify(appt.to_dict())

@doctor_bp.route('/appointments/<int:appt_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(appt_id):
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()
    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify(appt.to_dict())

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    patient_ids = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct().all()
    from ..models import Patient
    patients = [Patient.query.get(pid[0]) for pid in patient_ids]
    return jsonify([p.to_dict() for p in patients if p])

@doctor_bp.route('/patients/<int:pat_id>/history', methods=['GET'])
@doctor_required
def patient_history(pat_id):
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    appointments = Appointment.query.filter_by(doctor_id=doctor.id, patient_id=pat_id)\
        .order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments])

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    today = date.today()
    week_end = today + timedelta(days=7)
    avails = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end
    ).all()
    return jsonify([a.to_dict() for a in avails])

@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability():
    user_id = get_jwt_identity()
    doctor = User.query.get(int(user_id)).doctor
    data = request.get_json()
    date_str = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    is_available = data.get('is_available', True)
    max_appointments = data.get('max_appointments', 10)

    avail_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    existing = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=avail_date).first()

    if existing:
        existing.start_time = start_time
        existing.end_time = end_time
        existing.is_available = is_available
        existing.max_appointments = max_appointments
    else:
        avail = DoctorAvailability(
            doctor_id=doctor.id,
            date=avail_date,
            start_time=start_time,
            end_time=end_time,
            is_available=is_available,
            max_appointments=max_appointments
        )
        db.session.add(avail)
    db.session.commit()
    return jsonify({'message': 'Availability updated'})
