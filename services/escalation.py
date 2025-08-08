from flask import request, jsonify, current_app
from utils.user_map import user_chat_map, set_user_status, is_escalated
from utils.attachment_processor import process_attachments_for_ccai
from utils.dialogflow_utils import send_to_dialogflow, extract_dialogflow_responses, prepare_message_for_dialogflow, should_escalate_to_human
from config import Config


def handle_escalated_conversation(identifier, text, attachments):
    ccai_client = current_app.clients["ccai_client"]

    user_info = user_chat_map.get(identifier, {})
    chat_id = user_info.get("chat_id")
    
    if not chat_id:
        set_user_status(identifier, "bot")
        return jsonify({"text": "⚠️ Erro na conversa. Redirecionando para o assistente virtual."}), 200
    
    try:
        if text:
            result = ccai_client.send_message(
                chat_id=chat_id,
                from_user_id=1,
                content=text
            )
            print(f"Mensagem enviada para agente humano: {result}")
        if attachments:
            process_attachments_for_ccai(chat_id, attachments)
        return jsonify({"text": ""}), 200
    except Exception as e:
        print(f"Erro ao enviar mensagem para agente humano: {e}")
        return jsonify({"text": "❌ Erro ao comunicar com o agente. Tente novamente."}), 500

def handle_bot_conversation(event, identifier, text, attachments, sender):
    ccai_client = current_app.clients["ccai_client"]

    if is_escalated(identifier):
        return handle_escalated_conversation(identifier, text, attachments)
    
    try:
        space_name = event.get("space", {}).get("name", "")
        user_data = ccai_client.get_end_user_by_id(1)
        end_user_id = user_data.get("id")
        user_info = user_chat_map.get(identifier, {})
        chat_id = user_info.get("chat_id")
        status = user_info.get("status")

        if not chat_id or status == "finished":
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
        else:
            user_info["space_name"] = space_name
            user_chat_map[identifier] = user_info

        if text:
            ccai_client.send_message(
                chat_id=chat_id,
                from_user_id=1,
                content=text
            )
        if attachments:
            process_attachments_for_ccai(chat_id, attachments)

        message_text = prepare_message_for_dialogflow(text, attachments)
        dialogflow_response = send_to_dialogflow(identifier, message_text)
        
        if should_escalate_to_human(dialogflow_response):
            return handle_escalation_request(identifier, chat_id)
        if is_escalated(identifier):
            return handle_escalated_conversation(identifier, text, attachments)
        
        reply_texts = extract_dialogflow_responses(dialogflow_response)
        reply_text = "\n".join(reply_texts) if reply_texts else "Desculpe, não entendi."
        return jsonify({"text": message_text}), 200
        
    except Exception as e:
        print(f"Erro no fluxo do bot: {e}")
        return jsonify({"text": "❌ Ocorreu um erro ao processar a mensagem."}), 500

def handle_escalation_request(identifier, chat_id, body=None):
    ccai_client = current_app.clients["ccai_client"]

    try:
        escalation_result = ccai_client.escalate_chat_to_human(
            chat_id=chat_id,
            reason="Usuário solicitou atendimento humano",
            force_escalate=True
        )

        user_info = user_chat_map.get(identifier, {})
        user_info["status"] = "escalated"
        user_info["escalation_id"] = escalation_result.get("id")
        user_info["chat_id"] = chat_id
        user_chat_map[identifier] = user_info

        return jsonify({
            "text": "🔄 Estamos conectando você a um agente humano. Para otimizar seu tempo, por favor, informe o motivo do seu contato."
        }), 200
    except Exception as e:
        print(f"Erro ao escalar para humano: {e}")
        return jsonify({
            "text": "❌ Erro ao transferir para agente humano. Tente novamente."
        }), 500
