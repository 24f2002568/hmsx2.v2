from flask import Blueprint, jsonify
from ..models import Appointment

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/<int:appt_id>', methods=['GET'])
def get_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    return jsonify(appt.to_dict())
