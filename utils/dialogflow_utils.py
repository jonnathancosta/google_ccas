from google.cloud.dialogflowcx_v3beta1 import SessionsClient, QueryInput, TextInput, DetectIntentRequest
from utils.media_utils import get_media_type
from config import Config
from flask import current_app



def send_to_dialogflow(identifier, message_text):
    sessions_client = current_app.clients["sessions_client"]
    session_id = identifier.rsplit("/", 1)[-1]
    session_path = sessions_client.session_path(Config.PROJECT_ID, Config.LOCATION_ID, Config.AGENT_ID, session_id)
    query_input = QueryInput(
        text=TextInput(text=message_text),
        language_code=Config.LANG_CODE
    )
    request_dialogflow = DetectIntentRequest(
        session=session_path,
        query_input=query_input
    )
    return sessions_client.detect_intent(request=request_dialogflow)

def extract_dialogflow_responses(response):
    reply_texts = []
    if response.query_result.response_messages:
        for msg in response.query_result.response_messages:
            if hasattr(msg, "text") and msg.text.text:
                reply_texts.extend(msg.text.text)
    return reply_texts

def should_escalate_to_human(response):
    intent = response.query_result.intent.display_name.lower()
    if any(kw in intent for kw in ["humano", "agent", "escalation"]):
        return True

    parameters = response.query_result.parameters
    if parameters and "escalate_to_human" in parameters:
        return True
    reply_texts = extract_dialogflow_responses(response)
    for t in reply_texts:
        if any(k in t.lower() for k in ["transferir", "agente", "humano"]):
            return True
    return False

def prepare_message_for_dialogflow(text, attachments):
    media_info = ""
    if attachments:
        for attachment in attachments:
            content_type = attachment.get("contentType", "")
            content_name = attachment.get("contentName", "arquivo")
            media_type = get_media_type(content_type)
            if media_type == "image":
                media_info += f"Imagem: {content_name}\n"
            elif media_type == "audio":
                media_info += f"audio: {content_name}\n"
            elif media_type == "video":
                media_info += f"video: {content_name}\n"
            else:
                media_info += f"documento_arquivo: {content_name} (tipo: {content_type})\n"
    if media_info and text:
        return f"{text}\n\n{media_info}"
    elif media_info:
        return media_info
    return text


