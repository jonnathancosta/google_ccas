import os
from datetime import timedelta
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

# ------------------------------------------------------------
BUCKET_CCAI = os.getenv("BUCKET_CCAI")
# Caminho para a conta de serviço do CCAI
PATH_SERVICE_ACCOUNT = os.getenv("PATH_SERVICE_ACCOUNT")



MEDIA_TYPES = {
    "image": ["image/jpg", "image/png", "image/gif", "image/webp","image/jpeg"],
    "audio": ["audio/mpeg", "audio/ogg", "audio/wav", "audio/webm", "application/ogg"],
    "video": ["video/mp4", "video/webm", "video/ogg"],
    "document": [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain"
    ]
}


def get_media_type(content_type):
    """Identifica o tipo de mídia com base no content_type, rejeitando GIFs"""
    if content_type == "attachedGifs":
        return "Não suportamos."

    for media_type, types in MEDIA_TYPES.items():
        if any(content_type.startswith(t) for t in types) or content_type in types:
            return media_type
    return "unknown"

def get_photo(chat_id):
    """
    Busca a imagem mais recente do chat_id no bucket GCS, gera Signed URL e envia como card para o Google Chat.
    """
    try:
        storage_client = storage.Client.from_service_account_json(PATH_SERVICE_ACCOUNT)
        bucket = storage_client.bucket(BUCKET_CCAI)  # Usa o bucket de auditoria definido na variável de ambiente
        blobs = list(bucket.list_blobs())  # Sem prefixo para listar tudo
        search_pattern = f"chat-{chat_id}-photo-"
        
        blobs_do_chat = [
            blob for blob in blobs
            if search_pattern in blob.name and (
                blob.name.endswith(".jpg") or blob.name.endswith(".jpeg") or blob.name.endswith(".png")
            )
        ]

        if not blobs_do_chat:
            print("Nenhuma imagem encontrada para este chat.")
            return None

        blob_mais_recente = max(blobs_do_chat, key=lambda b: b.updated)
        signed_url = blob_mais_recente.generate_signed_url(expiration=timedelta(hours=5))
        print(f"Enviando imagem mais recente para o Google Chat: {signed_url}")
        return signed_url

    except Exception as e:
        print(f"Erro ao buscar/enviar imagem: {e}")
        return None
        
        
def get_video(chat_id):
    """
    Busca o vídeo mais recente do chat_id no bucket GCS, gera Signed URL e retorna.
    """
    try:
        storage_client = storage.Client.from_service_account_json(PATH_SERVICE_ACCOUNT)
        bucket = storage_client.bucket(BUCKET_CCAI)  # Usa o bucket de armazenamento do CCAI
        blobs = list(bucket.list_blobs())  # Sem prefixo para listar tudo
        search_pattern = f"chat-{chat_id}-video-"

        # Filtra blobs do chat e pega o mais recente (apenas vídeos suportados)
        blobs_do_chat = [
            blob for blob in blobs
            if search_pattern in blob.name and (
                blob.name.endswith(".mp4") or blob.name.endswith(".webm") or blob.name.endswith(".ogg")
            )
        ]

        if not blobs_do_chat:
            print("Nenhum vídeo encontrado para este chat.")
            return None

        # Ordena por data de atualização (mais recente primeiro)
        blob_mais_recente = max(blobs_do_chat, key=lambda b: b.updated)
        signed_url = blob_mais_recente.generate_signed_url(expiration=timedelta(hours=5))
        print(f"Enviando vídeo mais recente para o Google Chat: {signed_url}")
        return signed_url

    except Exception as e:
        print(f"Erro ao buscar/enviar vídeo: {e}")
        return None
        

def get_document(chat_id):
    """
    Busca o vídeo mais recente do chat_id no bucket GCS, gera Signed URL e retorna.
    """
    try:
        storage_client = storage.Client.from_service_account_json(PATH_SERVICE_ACCOUNT)
        bucket = storage_client.bucket(BUCKET_CCAI)  # Usa o bucket de auditoria definido na variável de ambiente
        blobs = list(bucket.list_blobs(prefix="media/"))
        search_pattern = f"chat-{chat_id}-document-"

        # Filtra blobs do chat e pega o mais recente
        blobs_do_chat = [blob for blob in blobs if search_pattern in blob.name]
        if not blobs_do_chat:
            print("Nenhum vídeo encontrado para este chat.")
            return

        # Ordena por data de atualização (mais recente primeiro)
        blob_mais_recente = max(blobs_do_chat, key=lambda b: b.updated)
        signed_url = blob_mais_recente.generate_signed_url(expiration=timedelta(hours=5))
        print(f"Enviando vídeo mais recente para o Google Chat: {signed_url}")
        return signed_url

    except Exception as e:
        print(f"Erro ao buscar/enviar vídeo: {e}")