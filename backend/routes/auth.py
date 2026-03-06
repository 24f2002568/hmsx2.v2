from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import User, Doctor, Patient, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    token = create_access_token(identity=str(user.id))
    
    profile_id = None
    if user.role == 'doctor' and user.doctor:
        profile_id = user.doctor.id
    elif user.role == 'patient' and user.patient:
        profile_id = user.patient.id

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile_id': profile_id
        }
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    gender = data.get('gender', '').strip()
    dob = data.get('dob', '')

    if not all([username, email, password, full_name]):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(username=username, email=email, role='patient')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        full_name=full_name,
        phone=phone,
        gender=gender,
        dob=datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = None
    if user.role == 'doctor' and user.doctor:
        profile = user.doctor.to_dict()
    elif user.role == 'patient' and user.patient:
        profile = user.patient.to_dict()

    return jsonify({'user': user.to_dict(), 'profile': profile})
