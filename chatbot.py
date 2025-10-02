"""
Chatbot 99Food - uazapiGO V2
Arquivo: chatbot.py (versão completa com debug e fallback)
"""

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

# ==================== CONFIGURAÇÕES ====================
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

def send_buttons(number, text, footer, buttons):
    """Envia mensagem com botões simples"""
    url = f"{API_HOST}/send/buttons"
    payload = {
        "number": number,
        "text": text,
        "footerText": footer,
        "buttons": buttons,
        "readchat": True,
        "readmessages": True,
        "delay": 1000
    }
    headers = {
        "Accept": "application/json",
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 ENVIANDO BOTÕES para {number}")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        print(f"✅ Status HTTP: {response.status_code}")
        print(f"📥 Resposta: {response.text[:200]}...")
        
        msg_status = response_data.get('status', 'unknown')
        if msg_status == 'Pending':
            print("⚠️  Mensagem ficou PENDENTE!")
        
        return response_data
    except Exception as e:
        print(f"❌ ERRO ao enviar botões: {e}")
        return None

def send_menu(number, text, footer, button_text, choices):
    """Envia menu com botões (mantido para compatibilidade)"""
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
    
    print(f"\n📤 ENVIANDO MENU para {number}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        print(f"✅ Status HTTP: {response.status_code}")
        print(f"📥 Resposta: {response.text[:200]}...")
        
        msg_status = response_data.get('status', 'unknown')
        if msg_status == 'Pending':
            print("⚠️  Mensagem ficou PENDENTE!")
        
        return response_data
    except Exception as e:
        print(f"❌ ERRO ao enviar menu: {e}")
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
    
    print(f"\n📤 ENVIANDO TEXTO para {number}")
    print(f"Mensagem: {text[:50]}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        print(f"✅ Status HTTP: {response.status_code}")
        
        msg_status = response_data.get('status', 'unknown')
        if msg_status == 'Pending':
            print("⚠️  Mensagem ficou PENDENTE!")
        
        return response_data
    except Exception as e:
        print(f"❌ ERRO ao enviar texto: {e}")
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
    
    print(f"\n📤 ENVIANDO VÍDEO para {number}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        print(f"✅ Status HTTP: {response.status_code}")
        
        msg_status = response_data.get('status', 'unknown')
        if msg_status == 'Pending':
            print("⚠️  Mensagem ficou PENDENTE!")
        
        return response_data
    except Exception as e:
        print(f"❌ ERRO ao enviar vídeo: {e}")
        return None

# ==================== FLUXO DO CHATBOT ====================

def iniciar_conversa(number):
    """Pergunta inicial"""
    print(f"\n🚀 INICIANDO conversa com {number}")
    
    # Tenta enviar com botões primeiro
    result = send_buttons(
        number=number,
        text="👋 Olá! Bem-vindo ao 99Food!\n\n🍕 Você já tem o app da 99Food instalado?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "SIM", "text": "✅ Sim, já tenho"},
            {"id": "NAO", "text": "📲 Não, preciso instalar"}
        ]
    )
    
    # Se falhar, envia texto simples
    if result and result.get('status') == 'Pending':
        print("⚠️ Botões falharam, enviando texto simples...")
        send_text(
            number,
            "👋 Olá! Bem-vindo ao 99Food!\n\n🍕 Você já tem o app da 99Food instalado?\n\n_Responda:_\n1️⃣ - Sim, já tenho\n2️⃣ - Não, preciso instalar"
        )
    
    user_states[number] = "AGUARDANDO_TEM_APP"

def nao_tem_app(number):
    """Envia link para download"""
    mensagem = f"""📲 *Sem problemas!*

Baixe o app da 99Food agora:

🔗 *Link do app:*
{LINK_APP_99FOOD}

Após instalar, volte aqui! 😊"""
    
    send_text(number, mensagem)
    
    result = send_buttons(
        number=number,
        text="Você já instalou o app?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "INSTALOU", "text": "✅ Sim, instalei!"},
            {"id": "DEPOIS", "text": "⏰ Vou instalar depois"}
        ]
    )
    
    if result and result.get('status') == 'Pending':
        send_text(number, "Você já instalou o app?\n\n1️⃣ - Sim, instalei!\n2️⃣ - Vou instalar depois")
    
    user_states[number] = "AGUARDANDO_INSTALACAO"

def tem_app(number):
    """Pergunta sobre cupom"""
    result = send_buttons(
        number=number,
        text="🎉 *Ótimo!*\n\n🎫 Você já utilizou algum cupom de desconto?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "JA_USEI", "text": "✅ Sim, já usei"},
            {"id": "NAO_USEI", "text": "🆕 Não, nunca usei"}
        ]
    )
    
    if result and result.get('status') == 'Pending':
        send_text(number, "🎉 *Ótimo!*\n\n🎫 Você já utilizou algum cupom de desconto?\n\n1️⃣ - Sim, já usei\n2️⃣ - Não, nunca usei")
    
    user_states[number] = "AGUARDANDO_CUPOM"

def enviar_tutorial(number):
    """Envia vídeo tutorial"""
    send_text(number, "📹 *Perfeito!*\n\nVou te ensinar como usar cupom!\n\nAssista o vídeo: 👇")
    
    send_video(
        number=number,
        video_url=VIDEO_TUTORIAL_URL,
        caption="🎬 Tutorial: Como usar cupom no 99Food"
    )
    
    result = send_buttons(
        number=number,
        text="📺 Assistiu o tutorial?\n\n✅ Conseguiu usar o cupom?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "DEU_CERTO", "text": "✅ Sim, consegui!"},
            {"id": "NAO_DEU_CERTO", "text": "❌ Não consegui"},
            {"id": "DEPOIS", "text": "⏰ Vou tentar depois"}
        ]
    )
    
    if result and result.get('status') == 'Pending':
        send_text(number, "📺 Assistiu o tutorial?\n\n✅ Conseguiu usar o cupom?\n\n1️⃣ - Sim, consegui!\n2️⃣ - Não consegui\n3️⃣ - Vou tentar depois")
    
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
    
    print(f"\n{'='*60}")
    print(f"⚙️ PROCESSANDO MENSAGEM")
    print(f"👤 Usuário: {number}")
    print(f"📊 Estado: {estado_atual}")
    print(f"💬 Mensagem: {message}")
    print(f"{'='*60}")
    
    if estado_atual == "INICIO":
        iniciar_conversa(number)
    
    elif estado_atual == "AGUARDANDO_TEM_APP":
        if "SIM" in msg or "1" in msg:
            tem_app(number)
        elif "NAO" in msg or "NÃO" in msg or "2" in msg:
            nao_tem_app(number)
    
    elif estado_atual == "AGUARDANDO_INSTALACAO":
        if "INSTALOU" in msg or "1" in msg:
            tem_app(number)
        else:
            send_text(number, "😊 Ok! Quando instalar, me avise!")
            if number in user_states:
                del user_states[number]
    
    elif estado_atual == "AGUARDANDO_CUPOM":
        if "JA_USEI" in msg or "JÁ" in msg or "1" in msg:
            enviar_grupo(number)
        elif "NAO_USEI" in msg or "NÃO" in msg or "2" in msg:
            enviar_tutorial(number)
    
    elif estado_atual == "AGUARDANDO_RESULTADO":
        if "DEU_CERTO" in msg or "1" in msg:
            deu_certo_tutorial(number)
        elif "NAO_DEU_CERTO" in msg or "NÃO" in msg or "2" in msg:
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
        
        print("\n" + "="*60)
        print(f"🔔 WEBHOOK RECEBIDO em {datetime.now()}")
        print("="*60)
        
        # LOG COMPLETO DOS DADOS RECEBIDOS
        print("📦 DADOS BRUTOS RECEBIDOS:")
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        print("="*60)
        
        # Ignora mensagens enviadas pelo próprio bot
        if data.get('message', {}).get('fromMe'):
            print("⚠️ IGNORADO - Mensagem enviada pelo bot")
            return jsonify({"status": "ignored - from me"}), 200
        
        # Extrai dados
        message_data = data.get('message', {})
        number = message_data.get('sender', '').replace('@s.whatsapp.net', '')
        message_text = message_data.get('text', '') or message_data.get('content', '')
        button_choice = message_data.get('buttonOrListid', '')
        
        print(f"📱 Número extraído: '{number}'")
        print(f"💬 Texto extraído: '{message_text}'")
        print(f"🔘 Botão extraído: '{button_choice}'")
        print(f"✅ Tem número? {bool(number)}")
        print(f"✅ Tem mensagem/botão? {bool(message_text or button_choice)}")
        
        if number and (message_text or button_choice):
            final_message = button_choice if button_choice else message_text
            print(f"🚀 PROCESSANDO: '{final_message}'")
            processar_mensagem(number, final_message)
            return jsonify({"status": "success"}), 200
        
        print("❌ ERRO - Dados incompletos ou inválidos")
        print(f"   - Número válido? {bool(number)}")
        print(f"   - Mensagem válida? {bool(message_text or button_choice)}")
        return jsonify({"error": "Dados incompletos"}), 400
    
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/test/<number>', methods=['GET'])
def testar(number):
    """Testa o bot manualmente"""
    print(f"\n🧪 TESTE MANUAL iniciado para {number}")
    iniciar_conversa(number)
    return jsonify({"status": "Iniciado", "number": number})

@app.route('/test-text/<number>', methods=['GET'])
def testar_texto(number):
    """Testa envio de texto simples"""
    print(f"\n🧪 TESTE DE TEXTO SIMPLES para {number}")
    
    # Remove caracteres especiais se tiver
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    print(f"📱 Número limpo: {number_clean}")
    
    result = send_text(number_clean, "🧪 Teste de conexão - Se você recebeu isso, o bot está funcionando!")
    
    return jsonify({
        "status": "Enviado",
        "number": number_clean,
        "result": result
    })

@app.route('/health', methods=['GET'])
def health():
    """Status do servidor"""
    return jsonify({
        "status": "online",
        "usuarios_ativos": len(user_states),
        "api_token_configured": API_TOKEN != 'SEU_TOKEN_AQUI',
        "timestamp": datetime.now().isoformat()
    })

# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    🤖 CHATBOT 99FOOD - UAZAPIGO V2
    ╚═══════════════════════════════════════╝
    
    ✅ Servidor rodando!
    
    📡 Endpoints:
    • POST /webhook - Recebe mensagens
    • GET  /test/<numero> - Testa bot
    • GET  /test-text/<numero> - Teste simples
    • GET  /health - Status
    
    🔧 Configure webhook: http://seu-ip:5000/webhook
    ╚═══════════════════════════════════════╝
    """)
    
    # Valida configuração
    if API_TOKEN == 'SEU_TOKEN_AQUI':
        print("⚠️  AVISO: API_TOKEN não configurado!")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)