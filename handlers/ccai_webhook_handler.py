from flask import request, jsonify
from services.ccai_events import (
    handle_ccai_message_received,
    handle_escalation_request,
    handle_ccai_escalation_created,
    handle_ccai_chat_ended,
    find_identifier_by_chat_id
)

def handle_ccai_webhooks():
    """
    Rota dedicada para webhooks do CCAI
    Processa eventos e envia mensagens de volta para o Google Chat
    """
    print("[ROUTE] /api/v1/ccai-webhook - Processando webhook do CCAI")

    event = request.get_json(silent=True)
    if not event:
        return jsonify({"status": "error", "message": "Payload inválido"}), 400

    required_ccai_fields = ["event_type", "chat_id", "body"]
    if not all(field in event for field in required_ccai_fields):
        return jsonify({"status": "error", "message": "Formato de webhook CCAI inválido"}), 400

    event_type = event["event_type"]
    chat_id = event["chat_id"]
    body = event.get("body", {})

    # Exemplo: buscar o identificador com o CCAI Client ou serviço
    identifier = find_identifier_by_chat_id(chat_id)
    if not identifier:
        print(f"[CCAI_WEBHOOK] Identifier não encontrado para chat_id: {chat_id}")
        return jsonify({"status": "ok"})

    # Processar diferentes tipos de eventos
    if event_type == "message_received":
        return handle_ccai_message_received(identifier, chat_id, body)

    elif event_type == "escalation_started":
        print(f"[CCAI_WEBHOOK] Escalação iniciada para {identifier}")
        return handle_escalation_request(identifier, chat_id, body)

    elif event_type == "escalation_accepted":
        return handle_ccai_escalation_created(identifier, chat_id, body)

    elif event_type == "participant_left" and body.get("type") == "agent":
        print("Agente saiu do chat")
        return handle_ccai_chat_ended(identifier, chat_id, body)

    return jsonify({"status": "ok"})
