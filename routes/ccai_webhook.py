from flask import Blueprint
from handlers.ccai_webhook_handler import handle_ccai_webhooks

ccai_webhook_bp = Blueprint('ccai_webhook', __name__)

@ccai_webhook_bp.route('/api/v1/ccai-webhook', methods=['POST'])
def route_ccai_webhook():
    return handle_ccai_webhooks()

