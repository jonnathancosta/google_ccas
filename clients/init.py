
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
import google.auth.transport.requests
from google.cloud.dialogflowcx_v3beta1 import SessionsClient
from google.api_core.client_options import ClientOptions
from clients.ccai_client import CCAIChatClient
from clients.media_manager import CCAIChatMediaManager

def initialize_clients():
    load_dotenv()
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    SCOPES = [os.getenv("SCOPES")]
    LOCATION_ID = os.getenv("DIALOGFLOW_CX_LOCATION_ID")
    CCAI_BASE_URL = os.getenv("CCAI_BASE_URL")
    CCAI_USERNAME = os.getenv("CCAI_USERNAME")
    CCAI_PASSWORD = os.getenv("CCAI_PASSWORD")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    os.environ['GOOGLE_CHAT_TOKEN'] = credentials.token

    client_opts = ClientOptions(api_endpoint=f"{LOCATION_ID}-dialogflow.googleapis.com:443")
    sessions_client = SessionsClient(client_options=client_opts)

    ccai_client = CCAIChatClient(
        base_url=CCAI_BASE_URL,
        username=CCAI_USERNAME,
        password=CCAI_PASSWORD
    )
    media_manager = CCAIChatMediaManager(ccai_client)

    return {
        "credentials": credentials,
        "sessions_client": sessions_client,
        "ccai_client": ccai_client,
        "media_manager": media_manager
    }
