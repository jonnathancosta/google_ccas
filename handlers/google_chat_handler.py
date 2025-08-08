from flask import request, jsonify
from datetime import datetime, time
from flask import request, jsonify, current_app
import pytz
from utils.user_map import is_escalated
from services.escalation import handle_escalated_conversation, handle_escalation_request
from utils.user_map import user_chat_map
from utils.message_sender import send_message_to_google_chat
from config import Config
from utils.commands import process_command



def end_chat_ccaas(chat_id):
    ccai_client = current_app.clients["ccai_client"]
    user_data = ccai_client.get_end_user_by_id(1)
    # Extrai os dados necessários
    end_user_id = user_data.get("id")

    response = ccai_client.update_chat(
        chat_id=chat_id,
        from_user_id=end_user_id,
        deflection_channel="",
        status="finished",
        escalation_id=""
    )
    print(f"Chat {chat_id} finalizado. {response}")


def handle_user_messages():
    ccai_client = current_app.clients["ccai_client"]
    print("[ROUTE] /api/v1/googlechat - Processando mensagem do usuário")
    event = request.get_json(silent=True)

    # --- TRATATIVA DE HORÁRIO ---
    tz = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(tz)
    inicio = time(8, 30)
    fim = time(23, 30)
    if not (inicio <= agora.time() <= fim):
        return jsonify({
            "text": "⏰ Nosso atendimento humano funciona das 8:30h às 16:30h. Obrigado pela compreensão!"
        }), 200

    if not event:
        return jsonify({"text": "Payload inválido."}), 400

    msg = event.get("message", {})
    sender = msg.get("sender", {})
    identifier = sender.get("name")
    text = msg.get("text", "").strip()
    attachments = msg.get("attachment", [])
    email = msg.get("sender", {}).get("email", "") 
    print(f"[INFO] Mensagem recebida de {identifier} ({email}): {text}")
    
    if text.lower().startswith("/nova_solicitacao"):
        user_info = user_chat_map.get(identifier, {})
        chat_id = user_info.get("chat_id")
        if chat_id:
            end_chat_ccaas(chat_id)  # Finaliza o chat atual
            user_info["status"] = "finished"
            user_chat_map[identifier] = user_info

        # --- Cria novo chat imediatamente ---
        sender_email = sender.get("email")
        sender_name = sender.get("displayName", "Usuário")
        user_data = ccai_client.get_end_user_by_id(1)
        end_user_id = user_data.get("id")
        space_name = event.get("space", {}).get("name", "")

        novo_chat = ccai_client.create_chat(
            end_user_id=end_user_id,
            menu_id=Config.CCAI_MENU_ID,
            lang=Config.LANG_CODE,
            email=sender_email,
            context={
                "identifier": identifier,
                "sender_name": sender_name
            },
        )
        novo_chat_id = novo_chat.get("id")
        user_chat_map[identifier] = {
            "chat_id": novo_chat_id,
            "end_user_id": end_user_id,
            "space_name": space_name
        }

        ccai_client.send_message(
            chat_id=novo_chat_id,
            from_user_id=1,
            content="oi"
        )
        send_message_to_google_chat(
            space_name=space_name,
            message_text="*🔄 Nova solicitação iniciada!*\nA conversa anterior foi finalizada, e estou pronta para te atender novamente."
        )
        return jsonify({
            "text": "Como posso ajudar a sua serventia hoje? Por favor, detalhe sua solicitação para que eu possa direcioná-la ou digite \"ajuda\" para explorar as opções disponíveis."
        }), 200
    # ... (comandos /nova_solicitacao e /fim permanecem)

    response = process_command(event)
    if response:
        return response

    if not text and not attachments:
        return jsonify({"text": "⚠️ Não recebi nenhum texto ou anexo para processar."}), 400

    # Se já está escalado, mantém o fluxo de humano
    if is_escalated(identifier):
        return handle_escalated_conversation(identifier, text, attachments)

    # NOVO: Sempre escalar para humano se não for comando
    user_info = user_chat_map.get(identifier, {})
    chat_id = user_info.get("chat_id")
    if not chat_id:
        # Cria chat se não existir
        user_data = ccai_client.get_end_user_by_id(1)
        end_user_id = user_data.get("id")
        space_name = event.get("space", {}).get("name", "")
        chat = ccai_client.create_chat(
            end_user_id=end_user_id,
            menu_id=Config.CCAI_MENU_ID,
            lang=Config.LANG_CODE,
            email=sender.get("email"),
            context={
                "identifier": identifier,
                "sender_name": sender.get("displayName", "Usuário")
            },
        )
        chat_id = chat.get("id")
        user_chat_map[identifier] = {
            "chat_id": chat_id,
            "end_user_id": end_user_id,
            "status": "bot",
            "space_name": space_name
        }

    # Escala para humano
    return handle_escalation_request(identifier, chat_id)
