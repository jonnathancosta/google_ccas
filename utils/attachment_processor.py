import os
from utils.media_utils import get_media_type
from flask import current_app


def download_drive_file(drive_file_id):
    
    """
    Baixa um arquivo do Google Drive pelo drive_file_id usando uma service account.
    Verifica se a SA tem acesso antes de tentar baixar.
    Mostra o link do arquivo se acessível.
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    from google.oauth2 import service_account
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)
    # Verificar acesso antes de tentar download
    try:
        file = drive_service.files().get(
            fileId=drive_file_id,
            fields='id, name, mimeType, webViewLink',
            supportsAllDrives=True
        ).execute()
        mime_type = file['mimeType']
        
        print(f"✅ Arquivo acessível: {file['name']} ({mime_type})")
        print(f"🔗 Link para visualização: {file['webViewLink']}")
    except Exception as e:
        print(f"🔗 Link para visualização: {file['webViewLink']}")
        raise Exception(
            f"❌ A Service Account não tem acesso ao arquivo {drive_file_id}.\n"
            f"📧 Compartilhe com: {creds.service_account_email}\n\n"
            f"Detalhes do erro: {e}",
        )

    # Baixar conteúdo
    try:
        if mime_type.startswith("application/vnd.google-apps.document"):
            # Google Docs → exporta para PDF
            request = drive_service.files().export_media(fileId=drive_file_id, mimeType="application/pdf")
        elif mime_type.startswith("application/vnd.google-apps.spreadsheet"):
            # Google Sheets → exporta para XLSX
            request = drive_service.files().export_media(fileId=drive_file_id, mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        elif mime_type.startswith("application/vnd.google-apps.presentation"):
            # Google Slides → exporta para PPTX
            request = drive_service.files().export_media(fileId=drive_file_id, mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        else:
            # Arquivo binário normal
            request = drive_service.files().get_media(fileId=drive_file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.getvalue()
    except Exception as e:
        raise Exception(f"❌ Falha ao baixar o arquivo: {e}")

def send_message_to_ccai(chat_id, content, from_user_id=1, message_type="text"):
    """
    Envia uma mensagem simples para o CCAI via ccai_client.
    """
    
    ccai_client = current_app.clients["ccai_client"]
    try:
        result = ccai_client.send_message(
            chat_id=chat_id,
            from_user_id=from_user_id,
            content=content,
            message_type=message_type
        )
        print(f"💬 Mensagem enviada para CCAI: {result}")
        return result
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para CCAI: {e}")
        return None

def process_attachments_for_ccai(chat_id, attachments):
    google_chat_token = os.environ.get("GOOGLE_CHAT_TOKEN")
    media_manager = current_app.clients["media_manager"]
    ccai_client = current_app.clients["ccai_client"]
    
    for attachment in attachments:
        content_type = attachment.get("contentType", "")
        media_type = get_media_type(content_type)
        resource_name = attachment.get("attachmentDataRef", {}).get("resourceName")
        content_name = attachment.get("contentName", "arquivo")
        drive_data = attachment.get("driveDataRef")

        try:
            # Caso seja anexo do Google Drive
            if drive_data:
                drive_file_id = drive_data.get("driveFileId")
                file_bytes = download_drive_file(drive_file_id)
                print(f"Media type: {media_type}, Content type: {content_type}, File name: {content_name}")
                # Decide o método conforme o tipo de mídia
                if media_type == "image":
                    result = media_manager.upload_and_add_photo_from_drive(
                        chat_id=chat_id,
                        image_bytes=file_bytes,
                        photo_type=content_type,
                        from_user_id=1
                    )
                    print(f"📷 Imagem enviada para CCAI: {result}")
                
                elif media_type == "document":
                    result = media_manager.upload_and_add_document_from_drive(
                        chat_id=chat_id,
                        document_bytes=file_bytes,
                        document_type=content_type,
                        from_user_id=1
                    )
                elif media_type == "video" or media_type == "audio":
                    result = media_manager.upload_and_add_video_from_drive(
                        chat_id=chat_id,
                        video_bytes=file_bytes,
                        video_type=content_type,
                        from_user_id=1
                    )
                else:
                    result = media_manager.send_message(
                        chat_id=chat_id,
                        from_user_id=1,
                        content=f"⚠️ O usuário tentou enviar um arquivo do Drive não suportado: {media_type} ({content_type})")
            
            if media_type == "image" and resource_name and google_chat_token:
                result = media_manager.upload_and_add_photo(
                    chat_id=chat_id,
                    resource_name=resource_name,
                    google_chat_token=google_chat_token,
                    from_user_id=1
                )
                print(f"🖼️ Imagem enviada para CCAI: {result}")

            elif media_type == "video" and resource_name and google_chat_token:
                result = media_manager.upload_and_add_video(
                    chat_id=chat_id,
                    resource_name=resource_name,
                    google_chat_token=google_chat_token,
                    from_user_id=1
                )
                print(f"🎥 Vídeo enviado para CCAI: {result}")

            elif media_type == "audio" and resource_name and google_chat_token:
                print("Enviando áudio diretamente como vídeo (sem conversão)...")
                result = media_manager.upload_and_add_video(
                    chat_id=chat_id,
                    resource_name=resource_name,
                    google_chat_token=google_chat_token,
                    from_user_id=1
                )
                print(f"🎙️ Áudio enviado como vídeo para CCAI: {result}")
            
            elif media_type == "document":
                            result = media_manager.upload_and_add_document(
                                chat_id=chat_id,
                                resource_name=resource_name,
                                google_chat_token=google_chat_token,
                                document_type=content_type,
                                from_user_id=1
                            )
        
            else:
                result = ccai_client.send_message(
                    chat_id=chat_id,
                    from_user_id=1,
                    content=f"[Arquivo recebido] {content_name}",
                    message_type="file"
                )

        except Exception as e:
            send_message_to_ccai(chat_id, "O usuario tentou enviar uma imagem do Drive, que não conseguimos processar")
            print(f"❌ Erro ao processar anexo ({media_type}): {e}")
            
