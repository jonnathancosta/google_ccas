import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()
BUCKET_EMPRESA = os.getenv("BUCKET_EMPRESA")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

class CCAIChatMediaManager:
    """
    Classe auxiliar para upload e registro de mídias (fotos e vídeos) no CCAI.
    """
    def __init__(self, chat_client):
        """
        Recebe uma instância de CCAIChatClient.
        """
        self.chat_client = chat_client

    def _request(self, method, endpoint, data=None, params=None, headers=None):
        """
        Encaminha a requisição para o chat_client.
        """
        return self.chat_client._request(method, endpoint, data, params, headers)

    def upload_and_add_video_from_drive(self, chat_id, video_bytes=None, video_type=None, from_user_id=None):
        
        video_content = video_bytes
       
        try:
            upload_info = self.set_pre_signed_video_upload_url(chat_id)
            upload_url = upload_info.get("url")
            fields = upload_info.get("fields", {})
            s3_path = fields.get("key")

            if not upload_url or not s3_path:
                    raise Exception("Não foi possível obter upload_url ou s3_path para vídeo.")

            files = {'file': (fields.get("key"), video_content)}
            data = fields.copy()
            data.pop("key", None)
            upload_resp = requests.post(upload_url, data=data, files=files)
            if upload_resp.status_code not in [200, 201, 204]:
                raise Exception(f"Falha ao fazer upload do vídeo: {upload_resp.text}")

            add_video_result = self.add_uploaded_video(chat_id, s3_path, video_type=None)
            # O retorno pode ser dict ou list, igual ao de foto
            if isinstance(add_video_result, list) and len(add_video_result) > 0 and "media_id" in add_video_result[0]:
                    media_id = add_video_result[0]["media_id"]
            elif isinstance(add_video_result, dict) and "media_id" in add_video_result:
                    media_id = add_video_result["media_id"]
            else:
                    raise Exception(f"Falha ao registrar vídeo e obter media_id. Resposta: {add_video_result}")

                # 4. Enviar mensagem com o vídeo no chat
            message_result = {
                "from_user_id": from_user_id or 1,
                "message": {
                    "type": "video",
                    "media_id": media_id
                }
            }
            url = f"{self.chat_client.base_url}/chats/{chat_id}/message"
                
            send_message_resp = requests.post(
                url=url, json=message_result, auth=self.chat_client.auth, headers=self.chat_client.headers
            )

            print("Payload enviado para mensagem de vídeo:", message_result)
            print("Status code resposta:", send_message_resp.status_code)
            print("Resposta texto:", send_message_resp.text)

            if send_message_resp.status_code not in [200, 201]:
                return {
                    "success": False,
                    "error": f"Erro ao enviar mensagem no chat: {send_message_resp.text}",
                    "media_id": media_id,
                        
                }

            try:
                ccai_message_response = send_message_resp.json()
            except Exception:
                ccai_message_response = None
            return {
                "success": True,
                "media_id": media_id,
                "ccai_message_response": ccai_message_response,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
            
    def upload_and_add_photo_from_drive(self, chat_id, image_bytes, photo_type=None, from_user_id=None):
        """
        Recebe bytes de imagem (baixada do Google Drive) e registra no chat do CCAI.
        (NÃO faz upload para bucket GCS
        """
        img_content = image_bytes

        # Upload no chat do CCAI (pré-assinado)
        try:
            
            upload_info = self.set_pre_signed_photo_url(chat_id)
            upload_url = upload_info.get("url")
            fields = upload_info.get("fields", {})
            s3_path = fields.get("key")

            if not upload_url or not s3_path:
                raise Exception("Não foi possível obter upload_url ou s3_path")

            files = {'file': (fields.get("key"), img_content)}
            data = fields.copy()
            data.pop("key", None)
            upload_resp = requests.post(upload_url, data=data, files=files)
            if upload_resp.status_code not in [200, 201, 204]:
                raise Exception(f"Falha ao fazer upload para o chat: {upload_resp.text}")
            print("📨 Enviando imagem com photo_type:", photo_type)
            add_photo_result = self.add_uploaded_photo(chat_id, s3_path, photo_type=None)
            print(f"Tipo de photo enviado: {add_photo_result[0].get('photo_type')}")
            if not add_photo_result or not isinstance(add_photo_result, list) or not add_photo_result[0].get("media_id"):
                raise Exception(f"Falha ao registrar foto e obter media_id. Resposta: {add_photo_result}")
            media_id = add_photo_result[0]["media_id"]
            print(f"   ✅ Foto registrada! Media ID: {media_id}")
            message_result = {
                "from_user_id": from_user_id or 1,
                "message": {
                    "type": "photo",
                    "media_id": media_id
                }
            }
            url = f"{self.chat_client.base_url}/chats/{chat_id}/message"
            send_message_resp = requests.post(
                url=url, json=message_result, auth=self.chat_client.auth, headers=self.chat_client.headers)

            print("Payload enviado para mensagem de imagem:", message_result)
            print("Status code resposta:", send_message_resp.status_code)
            print("Resposta texto:", send_message_resp.text)
            
            if send_message_resp.status_code not in [200, 201]:
                return {
                    "success": False,
                    "error": f"Erro ao enviar mensagem no chat: {send_message_resp.text}",
                    "media_id": media_id
                }

            try:
                ccai_message_response = send_message_resp.json()
            except Exception:
                ccai_message_response = None

            return {
                "success": True,
                "media_id": media_id,
                "ccai_message_response": ccai_message_response
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_and_add_document_from_drive(self, chat_id, document_bytes, document_type=None, from_user_id=None):
        """
        Baixa documento do Google Chat, registra e envia no chat do CCAI,
        e também envia para o bucket dev-ccaas-voice-recordings (auditoria).
        """
        document_content = document_bytes
        nome_arquivo = f"documento_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.bin"
        
        try:
            bucket_name = BUCKET_EMPRESA
            now = datetime.utcnow()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")
            timestamp = now.strftime("%Y%m%dT%H%M%S")
            blob_name = f"media/{year}/{month}/{day}/{chat_id}_{timestamp}_{nome_arquivo}"

            storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            # Detecta o content_type se possível
            content_type = document_type or "application/octet-stream"
            blob.upload_from_string(document_content, content_type=content_type)
            blob_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            audit_status = True

            # GERAÇÃO DA SIGNED URL PARA DOWNLOAD (válida por 5 hora)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=5),
                method="GET"
            )
        except Exception as e:
            blob_url = None
            audit_status = False
            audit_error = str(e)
            return {"success": False, "error": audit_error, "audit_status": audit_status, "blob_url": blob_url}

        # 3. Encurta o link
        short_url = encurtar_link_tinyurl(signed_url)

        # 4. Envia mensagem para o chat do CCAI
        if from_user_id is None:
            from_user_id = 1
        mensagem = f"📁 O Usuario enviou um arquivo: {short_url}"

        send_result = self.chat_client.send_message(
            chat_id=chat_id,
            from_user_id=from_user_id,
            content=mensagem,
            message_type="text"
        )

        return {"success": True, "mensagem_enviada": send_result}
    
    def upload_and_add_photo(self, chat_id, resource_name=None, image_bytes=None, photo_type=None, google_chat_token=None, from_user_id=None):
        """
        Baixa imagem do Google Chat, registra e envia no chat do CCAI,
        e também envia para o bucket ccai-data-conversation.
        """
        img_content = None

        # 1. Baixar imagem do Google Chat
        if resource_name and google_chat_token:
            url = f"https://chat.googleapis.com/v1/media/{resource_name}?alt=media"
            headers = {"Authorization": f"Bearer {google_chat_token}"}
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                return {"success": False, "error": f"Falha ao baixar imagem do Google Chat: {resp.text}"}
            img_content = resp.content
        elif image_bytes is not None:
            img_content = image_bytes
        else:
            return {"success": False, "error": "Nenhuma imagem fornecida"}

  

        # 3. Upload no chat do CCAI
        try:
            print("   [Passo 3/4] Registrando foto no chat para obter media_id...")
            upload_info = self.set_pre_signed_photo_url(chat_id)
            upload_url = upload_info.get("url")
            print(f"   [Passo 1/4] Obtendo URL pré-assinada para upload de foto: {upload_url} e {upload_info}")
            fields = upload_info.get("fields", {})
            s3_path = fields.get("key")

            if not upload_url or not s3_path:
                raise Exception("Não foi possível obter upload_url ou s3_path")

            files = {'file': (fields.get("key"), img_content)}
            data = fields.copy()
            data.pop("key", None)
            upload_resp = requests.post(upload_url, data=data, files=files)
            if upload_resp.status_code not in [200, 201, 204]:
                raise Exception(f"Falha ao fazer upload para o chat: {upload_resp.text}")
            
            add_photo_result = self.add_uploaded_photo(chat_id, s3_path, photo_type)
            print(f"Tipo de photo enviado: {add_photo_result[0].get('photo_type')}")
            if not add_photo_result or not isinstance(add_photo_result, list) or not add_photo_result[0].get("media_id"):
                raise Exception(f"Falha ao registrar foto e obter media_id. Resposta: {add_photo_result}")
            media_id = add_photo_result[0]["media_id"]
            print(f"   ✅ Foto registrada! Media ID: {media_id}")

            print("   [Passo 4/4] Enviando a foto como mensagem no chat...")
            message_result = {
                "from_user_id": from_user_id or 1,
                "message": {
                    "type": "photo",
                    "media_id": media_id
                }
            }
            url = f"{self.chat_client.base_url}/chats/{chat_id}/message"
            print(f"   Enviando mensagem para o chat {chat_id} com media_id {media_id}...")
            print(f"URL para enviar mensagem: {url}, Payload: {message_result}")
            send_message_resp = requests.post(
                url=url, json=message_result, auth=self.chat_client.auth, headers=self.chat_client.headers)
            
            print("Payload enviado para mensagem de imagem:", message_result)
            print("Status code resposta:", send_message_resp.status_code)
            print("Resposta texto:", send_message_resp.text)
            
            if send_message_resp.status_code not in [200, 201]:
                return {
                    "success": False,
                    "error": f"Erro ao enviar mensagem no chat: {send_message_resp.text}",
                    "media_id": media_id,
                   
                    
                }

            try:
                ccai_message_response = send_message_resp.json()
            except Exception:
                ccai_message_response = None
        
            return {
                    "success": True,
                    "media_id": media_id,
                    "ccai_message_response": ccai_message_response,                    
                    
                }

        except Exception as e:
            print(f"❌ ERRO durante upload para o chat: {e}")
            return {
                "success": False,
                "error": str(e),
                
            }
    
    def add_uploaded_photo(self, chat_id, s3_path, photo_type=None):
        photo_obj = {"s3_path": s3_path}
        if photo_type:
            photo_obj["photo_type"] = photo_type
        data = {"photo": [photo_obj]}
        return self._request("POST", f"/chats/{chat_id}/photos", data = data)
    
    def get_all_photos(self, chat_id):
        return self._request("GET", f"/chats/{chat_id}/photos")
    # Get a pre-signed URL for photo upload
    def set_pre_signed_photo_url(self, chat_id):
        return self._request("POST", f"/chats/{chat_id}/photos/upload")

    def set_pre_signed_photo_url_drive(self, chat_id, content_type=None):
        """
        Solicita uma URL pré-assinada para upload de imagem no chat,
        informando o content_type correto (ex: image/jpeg).
        """
        data = {}
        if content_type:
            data["content_type"] = content_type

        return self._request(
            method="POST",
            endpoint=f"/chats/{chat_id}/photos/upload",
            data=data,
            headers=self.chat_client.headers  # ou self.ccaiclient.headers se estiver usando esse nome
        )

    def upload_and_add_video(self, chat_id, resource_name=None, video_bytes=None, video_type=None, google_chat_token=None, from_user_id=None):
        """
        Baixa vídeo do Google Chat, registra e envia no chat do CCAI,
        e também envia para o bucket ccai-data-conversation (auditoria).
        """
        video_content = None

        # 1. Baixar vídeo do Google Chat
        if resource_name and google_chat_token:
            url = f"https://chat.googleapis.com/v1/media/{resource_name}?alt=media"
            headers = {"Authorization": f"Bearer {google_chat_token}"}
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                return {"success": False, "error": f"Falha ao baixar vídeo do Google Chat: {resp.text}"}
            video_content = resp.content
        elif video_bytes is not None:
            video_content = video_bytes
        else:
            return {"success": False, "error": "Nenhum vídeo fornecido"}

        # 3. Upload no chat do CCAI
        try:
            upload_info = self.set_pre_signed_video_upload_url(chat_id)
            upload_url = upload_info.get("url")
            fields = upload_info.get("fields", {})
            s3_path = fields.get("key")

            if not upload_url or not s3_path:
                raise Exception("Não foi possível obter upload_url ou s3_path para vídeo.")

            files = {'file': (fields.get("key"), video_content)}
            data = fields.copy()
            data.pop("key", None)
            upload_resp = requests.post(upload_url, data=data, files=files)
            if upload_resp.status_code not in [200, 201, 204]:
                raise Exception(f"Falha ao fazer upload do vídeo: {upload_resp.text}")

            add_video_result = self.add_uploaded_video(chat_id, s3_path, video_type)
            # O retorno pode ser dict ou list, igual ao de foto
            if isinstance(add_video_result, list) and len(add_video_result) > 0 and "media_id" in add_video_result[0]:
                media_id = add_video_result[0]["media_id"]
            elif isinstance(add_video_result, dict) and "media_id" in add_video_result:
                media_id = add_video_result["media_id"]
            else:
                raise Exception(f"Falha ao registrar vídeo e obter media_id. Resposta: {add_video_result}")

            # 4. Enviar mensagem com o vídeo no chat
            message_result = {
                "from_user_id": from_user_id or 1,
                "message": {
                    "type": "video",
                    "media_id": media_id
                }
            }
            url = f"{self.chat_client.base_url}/chats/{chat_id}/message"
            
            send_message_resp = requests.post(
                url=url, json=message_result, auth=self.chat_client.auth, headers=self.chat_client.headers
            )

            print("Payload enviado para mensagem de vídeo:", message_result)
            print("Status code resposta:", send_message_resp.status_code)
            print("Resposta texto:", send_message_resp.text)

            if send_message_resp.status_code not in [200, 201]:
                return {
                    "success": False,
                    "error": f"Erro ao enviar mensagem no chat: {send_message_resp.text}",
                    "media_id": media_id,
                     
                }

            try:
                ccai_message_response = send_message_resp.json()
            except Exception:
                ccai_message_response = None
            return {
                "success": True,
                "media_id": media_id,
                "ccai_message_response": ccai_message_response,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
            
    def set_pre_signed_video_upload_url(self, chat_id):
        return self._request("POST", f"/chats/{chat_id}/videos/upload")

    def add_uploaded_video(self, chat_id, s3_path, video_type=None):
        """
        Registra um vídeo previamente enviado via URL pré-assinada e retorna o media_id.
        """
        video_obj = {"s3_path": s3_path}
        if video_type:
            video_obj["type"] = video_type

        data = {"video": video_obj}
        try:
            response = self._request(
                "POST",
                f"/chats/{chat_id}/videos",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            return response  # <-- Retorne o dict diretamente!
        except requests.HTTPError as e:
            return {"success": False, "error": f"Falha ao registrar vídeo. Resposta: {e.response.text}"}
    
    def upload_and_add_document(self, chat_id, resource_name=None, document_bytes=None, document_type=None, google_chat_token=None, from_user_id=None):
        """
        Baixa documento do Google Chat, registra e envia no chat do CCAI,
        e também envia para o bucket dev-ccaas-voice-recordings (auditoria).
        """
        document_content = None

        # 1. Baixar documento do Google Chat
        if resource_name and google_chat_token:
            url = f"https://chat.googleapis.com/v1/media/{resource_name}?alt=media"
            headers = {"Authorization": f"Bearer {google_chat_token}"}
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                return {"success": False, "error": f"Falha ao baixar documento do Google Chat: {resp.text}"}
            document_content = resp.content
            nome_arquivo = resource_name.split("/")[-1]
        elif document_bytes is not None:
            document_content = document_bytes
            nome_arquivo = f"documento_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.bin"
        else:
            return {"success": False, "error": "Nenhum documento fornecido"}

        try:
            bucket_name = BUCKET_EMPRESA
            now = datetime.utcnow()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")
            timestamp = now.strftime("%Y%m%dT%H%M%S")
            blob_name = f"media/{year}/{month}/{day}/{chat_id}_{timestamp}_{nome_arquivo}"

            storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            # Detecta o content_type se possível
            content_type = document_type or "application/octet-stream"
            blob.upload_from_string(document_content, content_type=content_type)
            blob_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            audit_status = True

            # GERAÇÃO DA SIGNED URL PARA DOWNLOAD (válida por 5 hora)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=5),
                method="GET"
            )
        except Exception as e:
            blob_url = None
            audit_status = False
            audit_error = str(e)
            return {"success": False, "error": audit_error, "audit_status": audit_status, "blob_url": blob_url}

        # 3. Encurta o link
        short_url = encurtar_link_tinyurl(signed_url)

        # 4. Envia mensagem para o chat do CCAI
        if from_user_id is None:
            from_user_id = 1
        mensagem = f"📁 O Usuario enviou um arquivo: {short_url}"

        send_result = self.chat_client.send_message(
            chat_id=chat_id,
            from_user_id=from_user_id,
            content=mensagem,
            message_type="text"
        )

        return {"success": True, "mensagem_enviada": send_result}

def encurtar_link_tinyurl(long_url):
    api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    else:
        print("Erro ao encurtar link:", response.text)
        return long_url
