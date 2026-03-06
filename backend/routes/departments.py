from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Department, User, db
from .. import cache

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/', methods=['GET'])
@cache.cached(timeout=600, key_prefix='all_departments')  # cache 10 min
def get_departments():
    depts = Department.query.all()
    return jsonify([d.to_dict() for d in depts])

@departments_bp.route('/', methods=['POST'])
@jwt_required()
def add_department():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    data = request.get_json()
    dept = Department(name=data['name'], description=data.get('description', ''))
    db.session.add(dept)
    db.session.commit()
    cache.delete('all_departments')  # invalidate cache
    return jsonify(dept.to_dict()), 201

@departments_bp.route('/<int:dept_id>', methods=['PUT'])
@jwt_required()
def update_department(dept_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    dept = Department.query.get_or_404(dept_id)
    data = request.get_json()
    dept.name = data.get('name', dept.name)
    dept.description = data.get('description', dept.description)
    db.session.commit()
    cache.delete('all_departments')  # invalidate cache
    return jsonify(dept.to_dict())
