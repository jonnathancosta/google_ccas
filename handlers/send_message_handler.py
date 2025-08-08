from flask import request, jsonify
import re
from utils.message_sender import send_message_to_google_chat

def send_message_endpoint():
    """
    Nova rota para envio de mensagens para o Google Chat
    Usada pelo CCAI para enviar mensagens de volta para os usuários
    """
    print("[ROUTE] /api/v1/send-message - Enviando mensagem para usuário")
    
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"status": "error", "message": "Payload inválido"}), 400

    # Buscar space_name dos dados recebidos ou usar padrão
    space_name = data.get("space_name") or data.get("identifier")
    message = data.get("message")
    
    if not message:
        return jsonify({"status": "error", "message": "Message é obrigatório"}), 400

    # <br> → \n
    message = message.replace('<br>', '\n')
    # ***texto*** → *_texto_*
    message = re.sub(r'\*\*\*(.*?)\*\*\*', r'*_\1_*', message)
    # **texto** → *texto*
    message = re.sub(r'\*\*(.*?)\*\*', r'*\1*', message)
    # *texto* → _texto_
    message = re.sub(r'\*(.*?)\*', r'*\1*', message)


    # Enviar mensagem via Google Chat API
    success = send_message_to_google_chat(space_name, message)
    
    if success:
        return jsonify({"status": "success", "message": "Mensagem enviada com sucesso"})
    else:
        return jsonify({"status": "error", "message": "Falha ao enviar mensagem"}), 500