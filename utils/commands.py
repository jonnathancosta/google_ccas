from flask import jsonify
from utils.cards import *

def process_command(event):
    # Verifica se tem appCommandMetadata (botão / comando rápido)
    if "appCommandMetadata" in event:
        command_name = event["appCommandMetadata"].get("appCommandId", "")
        command_name = str(command_name).lstrip("/").lower()

        param = None
        msg = event.get("message", {})
        text = msg.get("text", "").strip()

        if "slashCommand" in event:
            param = event["slashCommand"].get("argumentText", "").strip()
        if not param:
            parts = text.split(" ", 1)
            param = parts[1] if len(parts) > 1 else None

        if command_name in ("1", "ajuda"):
            return jsonify({"text": gerar_ajuda()}), 200

        if command_name in ("2", "contatosuporte"):
            return card_contato_suporte(), 200

        if command_name in ("3", "notícias"):
            return card_notícias(), 200
        
        if command_name in  ("4", "plataformas"):
            return gerar_card_plataformas(), 200
            
        if command_name in ("5", "treinamentos"):
            return gerar_card_treinamento()

        return jsonify({"text": f"❓ Comando não reconhecido: /{command_name}"}), 200



    # Se não tem appCommandMetadata, trata comandos por texto começando com "/"
    msg = event.get("message", {})
    text = msg.get("text", "").strip()

    if text.startswith("/"):
        parts = text[1:].split(" ", 1)
        command = parts[0].lower()
        param = parts[1] if len(parts) > 1 else None

        if command in ("ajuda", "1"):
            return jsonify({"text": gerar_ajuda()}), 200

        if command == ("contatosuporte", "2"):
            return card_contato_suporte(), 200

        if command in  ("notícias", "3"):
            return card_notícias(), 200
        
        if command in  ("plataformas", "4"):
            return gerar_card_plataformas(), 200

        if command == ("treinamentos", "5"):
            return gerar_card_treinamento()

        return jsonify({"text": f"❓ Comando não reconhecido: /{command}"}), 200

    # Se não entrou em nenhum dos casos acima, retorna None para seguir fluxo normal
    return None

# ------------------------------------------------------------
# GERA RESPOSTA DE AJUDA
# ------------------------------------------------------------


COMMANDS = {
    "ajuda": {
        "description": "Exibe a descrição deste comando e apresenta o menu completo de comandos"
    },
    "contatosuporte": {
        "description": "Exibe os contatos de suporte (e-mail, telefone, horários de atendimento)"
    },
    "notícias": {
    "description": "Veja as últimas novidades, comunicados e atualizações do ONR. Fique por dentro das notícias do setor de Registro de Imóveis."
    },
    "plataformas": {
    "description": "Apresenta todas as plataformas digitais atualmente oferecidas pelo ONR aos Cartórios de Registro de Imóveis."
    },
    "treinamentos": {
    "description": "Agende treinamentos on-line com nossos especialistas para aprender a usar as plataformas ONR."
    }
    }


def gerar_ajuda():
    titulo = "*Como posso te ajudar?*"
    intro = (
        "Veja abaixo os comandos disponíveis para facilitar seu atendimento. "
        "Basta digitar o comando desejado no chat:"
    )

    comandos_titulo = "\n📌 *Comandos disponíveis:*"
    comandos = ""
    for cmd, dados in COMMANDS.items():
        comandos += f"• `/{cmd}` — {dados['description']}\n"

    return f"{titulo}\n\n{intro}\n{comandos_titulo}\n{comandos.strip()}"



