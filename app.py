from flask import Flask
from clients.init import initialize_clients
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do .env
load_dotenv()

# Cria a instância do Flask
app = Flask(__name__)

# Inicializa e anexa os clients ao app
app.clients = initialize_clients()

# Importa e registra os blueprints
from routes.googlechat import googlechat_bp
from routes.ccai_webhook import ccai_webhook_bp
from routes.send_message import send_message_bp

app.register_blueprint(googlechat_bp)
app.register_blueprint(ccai_webhook_bp)
app.register_blueprint(send_message_bp)

# Rota de saúde opcional
@app.route("/health")
def health_check():
    return {"status": "ok"}, 200

# Inicia o servidor
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
