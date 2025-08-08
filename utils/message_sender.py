import os
import requests

def send_message_to_google_chat(space_name, message_text=None, image_url=None, video_url=None, Agente=None, document_url=None):
    """
    Envia mensagem para o Google Chat via API.
    Se image_url for informado, envia como card de imagem.
    Se só message_text, envia como texto simples.
    """
    print("Enviando mensagem para o Google Chat...")
    url = f"https://chat.googleapis.com/v1/{space_name}/messages"
    headers = {
        'Authorization': f'Bearer {os.getenv("GOOGLE_CHAT_TOKEN")}',
        'Content-Type': 'application/json'
    }

    if image_url:
        payload = {
            "cardsV2": [
                {
                    "cardId": "img_card",
                    "card": {
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "image": {
                                            "imageUrl": image_url,
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    elif message_text:
        payload = {'text': message_text}
    elif video_url:
        payload = {
            "cardsV2": [
                {
                    "cardId": "video_msg",
                    "card": {
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": f"🎥 O Agente {Agente}, enviou um vídeo para você\n\nClique no botão abaixo para assistir ao vídeo:"
                                        }
                                    },
                                    {
                                        "buttonList": {
                                            "buttons": [
                                                {
                                                    "text": "▶ Click Aqui ◀",
                                                    "onClick": {
                                                        "openLink": {
                                                            "url": video_url
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    
    elif document_url:
        payload = {
            "cardsV2": [
                {
                    "cardId": "doc_card_v2",
                    "card": {
                        "header": {
                            "title": f"📎Documento enviando por {Agente}",
                            "imageUrl": "https://cdn-icons-png.flaticon.com/512/337/337946.png",  # Ícone de documento
                            "imageType": "CIRCLE"
                        },
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "decoratedText": {
                                            "startIcon": {
                                                "knownIcon": "DESCRIPTION"
                                            },
                                            "text": "<b>Arquivo disponível</b><br>Abrir documento para leitura",
                                            "button": {
                                                "text": "Visualizar",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": document_url
                                                    }
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

    else:
        print("Nada para enviar ao Google Chat.")
        return False

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 200