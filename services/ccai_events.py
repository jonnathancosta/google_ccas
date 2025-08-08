from flask import jsonify
from utils.user_map import find_identifier_by_chat_id, user_chat_map
from services.escalation import handle_escalation_request
from utils.message_sender import send_message_to_google_chat
from utils.media_utils import get_photo, get_video
from handlers.google_chat_handler import end_chat_ccaas
import requests
from config import Config

def process_ccai_event(event):
    event_type = event.get("event_type")
    chat_id = event.get("chat_id")
    body = event.get("body", {})

    identifier = find_identifier_by_chat_id(chat_id)
    if not identifier:
        print(f"[CCAI_WEBHOOK] Identifier não encontrado para chat_id: {chat_id}")
        return jsonify({"status": "ok"})

    # Roteia os eventos
    if event_type == "message_received":
        return handle_ccai_message_received(identifier, chat_id, body)
    elif event_type == "escalation_started":
        return handle_escalation_request(identifier, chat_id, body)
    elif event_type == "escalation_accepted":
        return handle_ccai_escalation_created(identifier, chat_id, body)
    elif event_type == "participant_left" and body.get("type") == "agent":
        return handle_ccai_chat_ended(identifier, chat_id, body)

    return jsonify({"status": "ok"})

def handle_ccai_message_received(identifier, chat_id, body):
    """Processa mensagens recebidas do CCAI e envia para o usuário"""
    sender = body.get("sender", {})
    sender_type = sender.get("type")
    agent = sender.get("agent", {})
    end_user = body.get("end_user", {})
    message_data = body.get("message", {})
    content = message_data.get("content", "")
    message_type = message_data.get("type", "")
    media_id = message_data.get("media_id")

    if end_user:
        identifier = end_user.get("identifier") or end_user.get("email") or identifier

    user_info = user_chat_map.get(identifier, {})
    space_name = user_info.get("space_name")

    # Se a mensagem veio de um agente
    if sender_type == "agent":
        user_info["status"] = "escalated"
        user_info["chat_id"] = chat_id
        user_info["agent_id"] = agent.get("id") if agent else None
        user_info["agent_name"] = agent.get("name") if agent else None
        user_chat_map[identifier] = user_info

        message_to_send = "" 
        
        # Se for mensagem de mídia (imagem, etc)
        if message_type == "photo" and media_id:
            fotos = get_photo(chat_id)
            send_message_to_google_chat(space_name, image_url=fotos)
            
        if message_type == "video" and media_id:
            videos = get_video(chat_id)
            send_message_to_google_chat(space_name, video_url=videos)

        elif content:
            message_to_send = content

        # Enviar mensagem via nova rota (incluindo space_name)
        if message_to_send:
            requests.post(f"{Config.URL_GOOGLE_CHAT}/api/v1/send-message", json={
                "identifier": identifier,
                "space_name": space_name,
                "message": message_to_send
            })

    return jsonify({"status": "ok"})

def handle_ccai_escalation_created(identifier, chat_id, body):
    """Processa escalação criada"""
    #agent_name = agent.get("name") or "o agente"
    user_info = user_chat_map.get(identifier, {})
    user_info["status"] = "escalated"
    user_info["chat_id"] = chat_id
    user_chat_map[identifier] = user_info
    # Envie a mensagem de conexão imediatamente
    connection_message = f"✅ Você foi conectado ao agente humano. Como posso ajudá-lo?"
    requests.post(f"{Config.URL_GOOGLE_CHAT}/api/v1/send-message", json={
        "identifier": identifier,
        "space_name": user_info.get("space_name"),
        "message": connection_message
    })
    return jsonify({"status": "ok"})

def handle_ccai_chat_ended(identifier, chat_id, body):
    """Processa finalização de chat e envia mensagem para o usuário"""
    agent = body.get("agent", {})
    agent_name = agent.get("name") or "o agente"
    user_info = user_chat_map.get(identifier, {})
    user_chat_map[identifier] = user_info
    
    
    end_chat_ccaas(chat_id)
    user_info["status"] = "finished"
    connection_message = f"👋 Atendimento finalizado por {agent_name}. Se precisar de ajuda novamente, é só me chamar"
    requests.post(f"{Config.URL_GOOGLE_CHAT}/api/v1/send-message", json={
        "identifier": identifier,
        "space_name": user_info.get("space_name"),
        "message": connection_message
    })

    return jsonify({"status": "ok"})
