import requests


class CCAIChatClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self, method, endpoint, data=None, params=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        headers = headers if headers is not None else self.headers

        response = requests.request(
            method,
            url,
            json=data,
            params=params,
            auth=self.auth,
            headers=headers
        )

        # Tenta retornar o JSON, mas trata caso não seja JSON
        try:
            return response.json()
        except Exception:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
    
    # Create a new chat session
    def create_chat(self, end_user_id, menu_id, lang="pt-BR", email=None, context=None, transcript=None):
        data = {
            "chat": {
                "menu_id": menu_id,
                "end_user_id": end_user_id,
                "email": email,
                "lang": lang,
                "context": context
            }
        }
        print(data)
        if email:
            data["chat"]["email"] = email
        if context:
            data["chat"]["context"] = context
        if transcript:
            data["chat"]["transcript"] = transcript

        return self._request("POST", "/chats", data)

    # Update an existing chat
    def update_chat(self, chat_id, from_user_id, deflection_channel, status, escalation_id):
        data = {
            "finished_by_user_id": from_user_id,
            "chat": {
                "deflection_channel": deflection_channel,
                "status": status,
                "escalation_id": escalation_id
            }
        }
        return self._request("PATCH", f"/chats/{chat_id}", data)

    # Send a message within a chat
    def send_message(self, chat_id, from_user_id, content, message_type="text"):
        data = {
            "from_user_id": from_user_id,
            "message": {
                "type": message_type,
                "content": content
            }
        }
        return self._request("POST", f"/chats/{chat_id}/message", data)

    # Escala o chat para um agente humano
    def escalate_chat_to_human(self, chat_id, reason="Usuário solicitou atendimento humano", force_escalate=True):
        data = {
            "reason": reason,
            "force_escalate": force_escalate
        }
        return self._request("POST", f"/chats/{chat_id}/escalations", data)

    def get_chat_messages(self, chat_id):
        url = f"{self.base_url}/chats/{chat_id}/messages"
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"success": False, "status_code": 404, "error": f"Chat {chat_id} não encontrado."}
            else:
                try:
                    return {"success": False, "status_code": response.status_code, "error": response.json()}
                except Exception:
                    return {"success": False, "status_code": response.status_code, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Update the status or details of an escalation
    def escalate_chat_to_human(self, chat_id, reason="talk_to_human", force_escalate=True):
        data = {
            "reason": reason,
            "force_escalate": force_escalate
        }
        return self._request("POST", f"/chats/{chat_id}/escalations", data)
    
    # Retrieve a chat ID using end user identifier
    def get_chat_id(self, end_user_identifier):
        params = {"end_user_identifier": end_user_identifier}
        response = self._request("GET", "/chats/chat_id", params=params)
        return response.get("chat_id")
    
    # Retorna os detalhes completos de um chat existente
    def get_chat_by_id(self, chat_id):
        return self._request("GET", f"/chats/{chat_id}")

    # Get reserved data attributes during a chat
    def get_reserved_data_attributes(self, chat_id):
        return self._request("GET", f"/chats/{chat_id}/reserved_data_attributes")

    # Update reserved data attributes during a chat
    def update_reserved_data_attributes(self, chat_id, attributes_data):
        return self._request("PUT", f"/chats/{chat_id}/reserved_data_attributes", attributes_data)

    # Retrieve an end user by ID (novo estilo que você pediu)
    def get_end_user_by_id(self, user_id):
        params = {"id": user_id}
        return self._request("GET", "/end_users", params=params)

    # Retrieve an end user by identifier (também útil para consistência)
    def get_end_user_by_identifier(self, identifier):
        params = {"identifier": identifier}
        return self._request("GET", "/end_users", params=params)

    def get_customer_flags(self, chat_id):
        return self._request("GET", f"/chats/{chat_id}/customer_flag")



