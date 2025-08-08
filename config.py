import os
from google.oauth2 import service_account

class Config:
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    SCOPES = [os.getenv("SCOPES")]
    LANG_CODE = "pt-BR"

    # CCAI
    CCAI_BASE_URL = os.getenv("CCAI_BASE_URL")
    CCAI_USERNAME = os.getenv("CCAI_USERNAME")
    CCAI_PASSWORD = os.getenv("CCAI_PASSWORD")
    CCAI_MENU_ID = int(os.getenv("CCAI_MENU_ID"))

    # Dialogflow
    DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_CX_PROJECT_ID")
    DIALOGFLOW_LOCATION_ID = os.getenv("DIALOGFLOW_CX_LOCATION_ID")
    DIALOGFLOW_AGENT_ID = os.getenv("DIALOGFLOW_CX_AGENT_ID")

    # Google Chat
    URL_GOOGLE_CHAT = os.getenv("URL_GOOGLE_CHAT")

def load_google_credentials():
    return service_account.Credentials.from_service_account_file(
        Config.SERVICE_ACCOUNT_FILE,
        scopes=Config.SCOPES
    )
