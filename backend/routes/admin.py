from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Doctor, Patient, Department, Appointment, db
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    from .. import cache
    cached = cache.get('admin_dashboard_stats')
    if cached:
        return jsonify(cached)

    total_doctors = Doctor.query.join(User).filter(User.is_active == True).count()
    total_patients = Patient.query.join(User).filter(User.is_active == True).count()
    total_appointments = Appointment.query.count()
    booked = Appointment.query.filter_by(status='Booked').count()
    completed = Appointment.query.filter_by(status='Completed').count()
    cancelled = Appointment.query.filter_by(status='Cancelled').count()

    result = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'booked': booked,
        'completed': completed,
        'cancelled': cancelled
    }
    cache.set('admin_dashboard_stats', result, timeout=120)  # 2 min
    return jsonify(result)

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    search = request.args.get('search', '')
    query = Doctor.query.join(User)
    if search:
        query = query.filter(
            (Doctor.full_name.ilike(f'%{search}%')) |
            (Doctor.specialization.ilike(f'%{search}%'))
        )
    doctors = query.all()
    return jsonify([d.to_dict() for d in doctors])

@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', 'doctor@123')
    full_name = data.get('full_name', '').strip()
    specialization = data.get('specialization', '').strip()
    department_id = data.get('department_id')
    phone = data.get('phone', '')
    bio = data.get('bio', '')
    experience_years = data.get('experience_years', 0)
    consultation_fee = data.get('consultation_fee', 0.0)

    if not all([username, email, full_name]):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    user = User(username=username, email=email, role='doctor')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(
        user_id=user.id,
        full_name=full_name,
        specialization=specialization,
        department_id=department_id,
        phone=phone,
        bio=bio,
        experience_years=experience_years,
        consultation_fee=consultation_fee
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor added', 'doctor': doctor.to_dict()}), 201

@admin_bp.route('/doctors/<int:doc_id>', methods=['PUT'])
@admin_required
def update_doctor(doc_id):
    doctor = Doctor.query.get_or_404(doc_id)
    data = request.get_json()
    for field in ['full_name', 'specialization', 'phone', 'bio', 'experience_years', 'consultation_fee', 'department_id']:
        if field in data:
            setattr(doctor, field, data[field])
    if 'email' in data:
        doctor.user.email = data['email']
    db.session.commit()
    return jsonify(doctor.to_dict())

@admin_bp.route('/doctors/<int:doc_id>/toggle', methods=['POST'])
@admin_required
def toggle_doctor(doc_id):
    doctor = Doctor.query.get_or_404(doc_id)
    doctor.user.is_active = not doctor.user.is_active
    db.session.commit()
    return jsonify({'is_active': doctor.user.is_active})

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    search = request.args.get('search', '')
    query = Patient.query.join(User)
    if search:
        query = query.filter(
            (Patient.full_name.ilike(f'%{search}%')) |
            (Patient.phone.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    patients = query.all()
    return jsonify([p.to_dict() for p in patients])

@admin_bp.route('/patients/<int:pat_id>', methods=['PUT'])
@admin_required
def update_patient(pat_id):
    patient = Patient.query.get_or_404(pat_id)
    data = request.get_json()
    for field in ['full_name', 'phone', 'address', 'blood_group', 'emergency_contact']:
        if field in data:
            setattr(patient, field, data[field])
    db.session.commit()
    return jsonify(patient.to_dict())

@admin_bp.route('/patients/<int:pat_id>/toggle', methods=['POST'])
@admin_required
def toggle_patient(pat_id):
    patient = Patient.query.get_or_404(pat_id)
    patient.user.is_active = not patient.user.is_active
    db.session.commit()
    return jsonify({'is_active': patient.user.is_active})

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_appointments():
    status = request.args.get('status', '')
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify([a.to_dict() for a in appointments])
