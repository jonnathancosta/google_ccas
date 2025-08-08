from flask import Blueprint
from handlers.google_chat_handler import handle_user_messages

googlechat_bp = Blueprint('googlechat', __name__)

@googlechat_bp.route('/api/v1/googlechat', methods=['POST'])
def route_googlechat():
    return handle_user_messages()
