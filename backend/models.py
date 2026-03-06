from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / doctor / patient
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('Doctor', back_populates='user', uselist=False)
    patient = db.relationship('Patient', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctors = db.relationship('Doctor', back_populates='department')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'doctors_count': len(self.doctors)
        }


class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    full_name = db.Column(db.String(150), nullable=False)
    specialization = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Float, default=0.0)

    user = db.relationship('User', back_populates='doctor')
    department = db.relationship('Department', back_populates='doctors')
    availabilities = db.relationship('DoctorAvailability', back_populates='doctor', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', back_populates='doctor')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'department': self.department.name if self.department else None,
            'department_id': self.department_id,
            'phone': self.phone,
            'bio': self.bio,
            'experience_years': self.experience_years,
            'consultation_fee': self.consultation_fee,
            'email': self.user.email if self.user else None,
            'is_active': self.user.is_active if self.user else False
        }


class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)  # "09:00"
    end_time = db.Column(db.String(10), nullable=False)    # "17:00"
    is_available = db.Column(db.Boolean, default=True)
    max_appointments = db.Column(db.Integer, default=10)

    doctor = db.relationship('Doctor', back_populates='availabilities')

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'is_available': self.is_available,
            'max_appointments': self.max_appointments
        }


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    blood_group = db.Column(db.String(5))
    emergency_contact = db.Column(db.String(100))

    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'dob': self.dob.isoformat() if self.dob else None,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'blood_group': self.blood_group,
            'emergency_contact': self.emergency_contact,
            'email': self.user.email if self.user else None,
            'username': self.user.username if self.user else None,
            'is_active': self.user.is_active if self.user else False
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='Booked')  # Booked / Completed / Cancelled
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    treatment = db.relationship('Treatment', back_populates='appointment', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'doctor_name': self.doctor.full_name if self.doctor else None,
            'doctor_specialization': self.doctor.specialization if self.doctor else None,
            'date': self.date.isoformat(),
            'time': self.time,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat(),
            'treatment': self.treatment.to_dict() if self.treatment else None
        }


class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointment = db.relationship('Appointment', back_populates='treatment')

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'notes': self.notes,
            'next_visit': self.next_visit.isoformat() if self.next_visit else None,
            'created_at': self.created_at.isoformat()
        }
