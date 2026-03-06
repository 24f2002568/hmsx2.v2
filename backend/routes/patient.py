from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Patient, Doctor, Appointment, DoctorAvailability, db
from datetime import datetime, date, timedelta
from functools import wraps
import csv, io

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        return f(*args, **kwargs)
    return decorated

@patient_bp.route('/profile', methods=['GET'])
@patient_required
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return jsonify({'profile': user.patient.to_dict() if user.patient else None})

@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    patient = user.patient
    data = request.get_json()
    for field in ['full_name', 'phone', 'address', 'blood_group', 'emergency_contact', 'gender']:
        if field in data:
            setattr(patient, field, data[field])
    if 'dob' in data and data['dob']:
        patient.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(patient.to_dict())

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def search_doctors():
    from .. import cache
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

    # Only cache the unfiltered list (no search params)
    if not search and not specialization:
        cached = cache.get('all_active_doctors')
        if cached:
            return jsonify(cached)

    query = Doctor.query.join(User).filter(User.is_active == True)
    if search:
        query = query.filter(
            (Doctor.full_name.ilike(f'%{search}%')) |
            (Doctor.specialization.ilike(f'%{search}%'))
        )
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    doctors = query.all()
    result = [d.to_dict() for d in doctors]

    if not search and not specialization:
        cache.set('all_active_doctors', result, timeout=300)  # 5 min

    return jsonify(result)

@patient_bp.route('/doctors/<int:doc_id>/availability', methods=['GET'])
@patient_required
def doctor_availability(doc_id):
    today = date.today()
    week_end = today + timedelta(days=7)
    avails = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doc_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end,
        DoctorAvailability.is_available == True
    ).all()
    result = []
    for av in avails:
        booked = Appointment.query.filter_by(
            doctor_id=doc_id, date=av.date, status='Booked'
        ).count()
        av_dict = av.to_dict()
        av_dict['booked_count'] = booked
        av_dict['slots_remaining'] = av.max_appointments - booked
        result.append(av_dict)
    return jsonify(result)

@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments():
    user_id = get_jwt_identity()
    patient = User.query.get(int(user_id)).patient
    filter_type = request.args.get('filter', 'all')
    today = date.today()

    query = Appointment.query.filter_by(patient_id=patient.id)
    if filter_type == 'upcoming':
        query = query.filter(Appointment.date >= today, Appointment.status == 'Booked')
    elif filter_type == 'past':
        query = query.filter(Appointment.date < today)

    appointments = query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments])

@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment():
    user_id = get_jwt_identity()
    patient = User.query.get(int(user_id)).patient
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    time_str = data.get('time')
    reason = data.get('reason', '')

    appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Check conflict
    conflict = Appointment.query.filter_by(
        doctor_id=doctor_id, date=appt_date, time=time_str, status='Booked'
    ).first()
    if conflict:
        return jsonify({'error': 'This time slot is already booked'}), 409

    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        date=appt_date,
        time=time_str,
        status='Booked',
        reason=reason
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify(appt.to_dict()), 201

@patient_bp.route('/appointments/<int:appt_id>/cancel', methods=['POST'])
@patient_required
def cancel_appointment(appt_id):
    user_id = get_jwt_identity()
    patient = User.query.get(int(user_id)).patient
    appt = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first_or_404()
    if appt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be cancelled'}), 400
    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify(appt.to_dict())

@patient_bp.route('/appointments/<int:appt_id>/reschedule', methods=['POST'])
@patient_required
def reschedule_appointment(appt_id):
    user_id = get_jwt_identity()
    patient = User.query.get(int(user_id)).patient
    appt = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first_or_404()
    if appt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be rescheduled'}), 400
    data = request.get_json()
    new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    new_time = data['time']

    conflict = Appointment.query.filter_by(
        doctor_id=appt.doctor_id, date=new_date, time=new_time, status='Booked'
    ).filter(Appointment.id != appt_id).first()
    if conflict:
        return jsonify({'error': 'This time slot is already booked'}), 409

    appt.date = new_date
    appt.time = new_time
    db.session.commit()
    return jsonify(appt.to_dict())

@patient_bp.route('/export-csv', methods=['GET'])
@patient_required
def export_csv():
    user_id = get_jwt_identity()
    patient = User.query.get(int(user_id)).patient
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Appointment ID', 'Date', 'Time', 'Doctor', 'Specialization', 'Status', 'Reason', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'])
    for a in appointments:
        t = a.treatment
        writer.writerow([
            a.id, a.date, a.time, a.doctor.full_name, a.doctor.specialization,
            a.status, a.reason or '',
            t.diagnosis if t else '', t.prescription if t else '',
            t.notes if t else '', t.next_visit if t else ''
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'treatment_history_{patient.full_name}.csv'
    )
