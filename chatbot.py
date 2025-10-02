"""
Chatbot 99Food - uazapiGO V2
Arquivo: chatbot.py
"""

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

# ==================== CONFIGURAÇÕES ====================
# Usa variáveis de ambiente (Render) ou valores padrão
API_HOST = os.getenv('API_HOST', 'https://99food.uazapi.com')
API_TOKEN = os.getenv('API_TOKEN', 'SEU_TOKEN_AQUI')

LINK_APP_99FOOD = os.getenv('LINK_APP_99FOOD', 'https://seu-link-unico-aqui.com')
VIDEO_TUTORIAL_URL = os.getenv('VIDEO_TUTORIAL_URL', 'https://exemplo.com/tutorial.mp4')
LINK_GRUPO_OFERTAS = os.getenv('LINK_GRUPO_OFERTAS', 'https://chat.whatsapp.com/seu-link-grupo')

PORT = int(os.getenv('PORT', 5000))
# ====================================================================

app = Flask(__name__)
user_states = {}

# ==================== FUNÇÕES DE ENVIO ====================

def send_menu(number, text, footer, button_text, choices):
    """Envia menu com botões"""
    url = f"{API_HOST}/send/menu"
    payload = {
        "number": number,
        "type": "list",
        "text": text,
        "footerText": footer,
        "listButton": button_text,
        "selectableCount": 1,
        "choices": choices,
        "readchat": True,
        "readmessages": True,
        "delay": 1000
    }
    headers = {
        "Accept": "application/json",
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Erro: {e}")
        return None

def send_text(number, text):
    """Envia mensagem de texto"""
    url = f"{API_HOST}/send/text"
    payload = {
        "number": number,
        "text": text,
        "readchat": True,
        "readmessages": True,
        "delay": 1000
    }
    headers = {
        "Accept": "application/json",
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Erro: {e}")
        return None

def send_video(number, video_url, caption=""):
    """Envia vídeo como mídia"""
    url = f"{API_HOST}/send/video"
    payload = {
        "number": number,
        "video": video_url,
        "caption": caption,
        "readchat": True,
        "readmessages": True,
        "delay": 1000
    }
    headers = {
        "Accept": "application/json",
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Erro: {e}")
        return None

# ==================== FLUXO DO CHATBOT ====================

def iniciar_conversa(number):
    """Pergunta inicial"""
    send_menu(
        number=number,
        text="👋 Olá! Bem-vindo ao 99Food!\n\n🍕 Você já tem o app da 99Food instalado?",
        footer="Chatbot 99Food",
        button_text="📱 Responder",
        choices=[
            "Sim, já tenho|SIM|✅ App instalado",
            "Não, ainda não|NAO|📲 Preciso instalar"
        ]
    )
    user_states[number] = "AGUARDANDO_TEM_APP"

def nao_tem_app(number):
    """Envia links para download"""
    mensagem = f"""📲 *Sem problemas!*

Baixe o app da 99Food:

🤖 *Android:*
{LINK_PLAY_STORE}

🍎 *iPhone:*
{LINK_APP_STORE}

Após instalar, volte aqui! 😊"""
    
    send_text(number, mensagem)
    
    send_menu(
        number=number,
        text="Você já instalou o app?",
        footer="Chatbot 99Food",
        button_text="Responder",
        choices=[
            "Sim, instalei!|INSTALOU|✅ Instalado",
            "Vou instalar depois|DEPOIS|⏰ Mais tarde"
        ]
    )
    user_states[number] = "AGUARDANDO_INSTALACAO"

def tem_app(number):
    """Pergunta sobre cupom"""
    send_menu(
        number=number,
        text="🎉 *Ótimo!*\n\n🎫 Você já utilizou algum cupom de desconto?",
        footer="Chatbot 99Food",
        button_text="💬 Responder",
        choices=[
            "Sim, já usei|JA_USEI|✅ Já usei",
            "Não, ainda não|NAO_USEI|🆕 Nunca usei"
        ]
    )
    user_states[number] = "AGUARDANDO_CUPOM"

def enviar_tutorial(number):
    """Envia vídeo tutorial"""
    send_text(number, "📹 *Perfeito!*\n\nVou te ensinar como usar cupom!\n\nAssista o vídeo: 👇")
    
    send_video(
        number=number,
        video_url=VIDEO_TUTORIAL_URL,
        caption="🎬 Tutorial: Como usar cupom no 99Food"
    )
    
    send_menu(
        number=number,
        text="📺 Assistiu o tutorial?\n\n✅ Conseguiu usar o cupom?",
        footer="Chatbot 99Food",
        button_text="Responder",
        choices=[
            "Sim, deu certo!|DEU_CERTO|✅ Consegui",
            "Não consegui|NAO_DEU_CERTO|❌ Dificuldade",
            "Vou tentar depois|DEPOIS|⏰ Mais tarde"
        ]
    )
    user_states[number] = "AGUARDANDO_RESULTADO"

def enviar_grupo(number):
    """Envia link do grupo"""
    mensagem = f"""🎉 *Parabéns!*

Você está aproveitando o 99Food! 🍕

💰 *Quer mais ofertas?*

Entre no grupo VIP:
• 🎁 Cupons exclusivos
• 🔥 Ofertas relâmpago
• 💸 Descontos até 50%

👥 *Link do grupo:*
{LINK_GRUPO_OFERTAS}

Aproveite! 🚀"""
    
    send_text(number, mensagem)
    if number in user_states:
        del user_states[number]

def deu_certo_tutorial(number):
    """Sucesso após tutorial"""
    mensagem = f"""🎊 *Excelente!*

Fico feliz que deu certo! 🙌

💡 Entre no grupo de ofertas:

👥 *Link:*
{LINK_GRUPO_OFERTAS}

Nos vemos lá! 🚀"""
    
    send_text(number, mensagem)
    if number in user_states:
        del user_states[number]

def nao_deu_certo_tutorial(number):
    """Dificuldade após tutorial"""
    mensagem = """😔 Que pena!

📞 *Vamos te ajudar:*

1️⃣ Assista novamente
2️⃣ Copie o cupom corretamente
3️⃣ Cole antes de finalizar

💬 Suporte: suporte@99food.com

Me mande mensagem se precisar! 😊"""
    
    send_text(number, mensagem)
    if number in user_states:
        del user_states[number]

# ==================== PROCESSAMENTO ====================

def processar_mensagem(number, message):
    """Processa mensagens e gerencia fluxo"""
    
    estado_atual = user_states.get(number, "INICIO")
    msg = message.upper().strip()
    
    print(f"[{datetime.now()}] User: {number} | Estado: {estado_atual} | Msg: {message}")
    
    if estado_atual == "INICIO":
        iniciar_conversa(number)
    
    elif estado_atual == "AGUARDANDO_TEM_APP":
        if "SIM" in msg:
            tem_app(number)
        elif "NAO" in msg or "NÃO" in msg:
            nao_tem_app(number)
    
    elif estado_atual == "AGUARDANDO_INSTALACAO":
        if "INSTALOU" in msg:
            tem_app(number)
        else:
            send_text(number, "😊 Ok! Quando instalar, me avise!")
            if number in user_states:
                del user_states[number]
    
    elif estado_atual == "AGUARDANDO_CUPOM":
        if "JA_USEI" in msg or "JÁ" in msg:
            enviar_grupo(number)
        elif "NAO_USEI" in msg or "NÃO" in msg:
            enviar_tutorial(number)
    
    elif estado_atual == "AGUARDANDO_RESULTADO":
        if "DEU_CERTO" in msg:
            deu_certo_tutorial(number)
        elif "NAO_DEU_CERTO" in msg or "NÃO" in msg:
            nao_deu_certo_tutorial(number)
        else:
            send_text(number, "😊 Sem pressa! Quando testar, me avise!")
            if number in user_states:
                del user_states[number]
    
    else:
        iniciar_conversa(number)

# ==================== ROTAS ====================

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe mensagens via webhook"""
    try:
        data = request.json
        
        # Extrai número e mensagem (ajuste conforme seu webhook)
        number = data.get('from') or data.get('number', '').replace('@s.whatsapp.net', '')
        message = data.get('message') or data.get('text') or data.get('body', '')
        
        if number and message:
            processar_mensagem(number, message)
            return jsonify({"status": "success"}), 200
        
        return jsonify({"error": "Dados incompletos"}), 400
    
    except Exception as e:
        print(f"[ERRO] {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test/<number>', methods=['GET'])
def testar(number):
    """Testa o bot manualmente"""
    iniciar_conversa(number)
    return jsonify({"status": "Iniciado", "number": number})

@app.route('/health', methods=['GET'])
def health():
    """Status do servidor"""
    return jsonify({
        "status": "online",
        "usuarios_ativos": len(user_states),
        "timestamp": datetime.now().isoformat()
    })

# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("""
    ═══════════════════════════════════════
    🤖 CHATBOT 99FOOD - UAZAPIGO V2
    ═══════════════════════════════════════
    
    ✅ Servidor rodando!
    
    📡 Endpoints:
    • POST /webhook - Recebe mensagens
    • GET  /test/<numero> - Testa bot
    • GET  /health - Status
    
    🔧 Configure webhook: http://seu-ip:5000/webhook
    ═══════════════════════════════════════
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)