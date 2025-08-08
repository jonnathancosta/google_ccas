from flask import Blueprint
from handlers.send_message_handler import send_message_endpoint

send_message_bp = Blueprint('send_message', __name__)

@send_message_bp.route('/api/v1/send-message', methods=['POST'])
def route_send_message():
    return send_message_endpoint()
