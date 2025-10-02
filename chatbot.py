"""
Chatbot 99Food - uazapiGO V2
Arquivo: chatbot.py (VERSÃO COMPLETA E ATUALIZADA)
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
    print(f"📝 Mensagem: {text[:100]}...")
    print(f"🔑 Token: {API_TOKEN[:10]}...{API_TOKEN[-5:]}")
    print(f"🌐 URL: {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"\n📊 RESPOSTA DA API:")
        print(f"   Status HTTP: {response.status_code}")
        print(f"   Resposta completa: {response.text}")
        
        try:
            response_data = response.json()
            msg_status = response_data.get('status', 'unknown')
            
            if response.status_code == 200:
                print(f"   ✅ SUCESSO!")
            else:
                print(f"   ⚠️ Status não é 200")
                
            if msg_status == 'Pending':
                print(f"   ⚠️ Mensagem ficou PENDENTE (status: {msg_status})")
            elif msg_status == 'error':
                print(f"   ❌ ERRO na API: {response_data.get('message', 'Erro desconhecido')}")
                
            return response_data
        except:
            print(f"   ❌ ERRO ao parsear JSON da resposta")
            return {"status": "error", "raw": response.text}
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ TIMEOUT - API não respondeu em 10s")
        return None
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return None

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
    print(f"🔑 Token: {API_TOKEN[:10]}...{API_TOKEN[-5:]}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"\n📊 RESPOSTA DA API (BOTÕES):")
        print(f"   Status HTTP: {response.status_code}")
        print(f"   Resposta: {response.text[:300]}")
        
        response_data = response.json()
        msg_status = response_data.get('status', 'unknown')
        
        if msg_status == 'Pending' or response.status_code != 200:
            print(f"   ⚠️ FALHA nos botões - Usando texto simples como fallback")
            return None
            
        return response_data
    except Exception as e:
        print(f"   ❌ ERRO ao enviar botões: {e}")
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
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_data = response.json()
        
        print(f"   Status HTTP: {response.status_code}")
        
        return response_data
    except Exception as e:
        print(f"   ❌ ERRO ao enviar vídeo: {e}")
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
    if not result or result.get('status') == 'Pending':
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
    
    if not result or result.get('status') == 'Pending':
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
    
    if not result or result.get('status') == 'Pending':
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
    
    if not result or result.get('status') == 'Pending':
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
    print(f"📊 Estado atual: {estado_atual}")
    print(f"💬 Mensagem recebida: '{message}'")
    print(f"🔠 Mensagem normalizada: '{msg}'")
    print(f"{'='*60}")
    
    # Se não tem estado ou é uma saudação inicial, inicia conversa
    if estado_atual == "INICIO" or number not in user_states:
        print("   → Ação: Iniciar conversa (primeiro contato)")
        iniciar_conversa(number)
        return
    
    elif estado_atual == "AGUARDANDO_TEM_APP":
        print(f"   → Verificando resposta...")
        
        if "SIM" in msg or msg == "1":
            print("   → Ação: Usuário TEM o app")
            tem_app(number)
        elif "NAO" in msg or "NÃO" in msg or msg == "2":
            print("   → Ação: Usuário NÃO TEM o app")
            nao_tem_app(number)
        else:
            print("   → Ação: Resposta não reconhecida, repetindo pergunta")
            send_text(
                number,
                "🤔 Não entendi sua resposta.\n\nPor favor, escolha uma opção:\n\n1️⃣ - Sim, já tenho o app\n2️⃣ - Não, preciso instalar"
            )
        return
    
    elif estado_atual == "AGUARDANDO_INSTALACAO":
        print(f"   → Verificando instalação...")
        
        if "INSTALOU" in msg or msg == "1":
            print("   → Ação: Usuário instalou")
            tem_app(number)
        else:
            print("   → Ação: Usuário vai instalar depois")
            send_text(number, "😊 Ok! Quando instalar, me mande uma mensagem! Até logo! 👋")
            if number in user_states:
                del user_states[number]
        return
    
    elif estado_atual == "AGUARDANDO_CUPOM":
        print(f"   → Verificando uso de cupom...")
        
        if "JA" in msg or "JÁ" in msg or msg == "1":
            print("   → Ação: Usuário JÁ USOU cupom")
            enviar_grupo(number)
        elif "NAO" in msg or "NÃO" in msg or msg == "2":
            print("   → Ação: Usuário NUNCA USOU cupom")
            enviar_tutorial(number)
        else:
            print("   → Ação: Resposta não reconhecida")
            send_text(
                number,
                "🤔 Não entendi.\n\nVocê já usou cupom no 99Food?\n\n1️⃣ - Sim, já usei\n2️⃣ - Não, nunca usei"
            )
        return
    
    elif estado_atual == "AGUARDANDO_RESULTADO":
        print(f"   → Verificando resultado do tutorial...")
        
        if "DEU_CERTO" in msg or msg == "1" or "CONSEGUI" in msg:
            print("   → Ação: Tutorial DEU CERTO")
            deu_certo_tutorial(number)
        elif "NAO_DEU_CERTO" in msg or msg == "2" or "NAO CONSEGUI" in msg or "NÃO CONSEGUI" in msg:
            print("   → Ação: Tutorial NÃO DEU CERTO")
            nao_deu_certo_tutorial(number)
        else:
            print("   → Ação: Vai tentar depois")
            send_text(number, "😊 Sem pressa! Quando testar, me avise! Até logo! 👋")
            if number in user_states:
                del user_states[number]
        return
    
    else:
        print("   → Estado desconhecido, reiniciando")
        iniciar_conversa(number)

def processar_webhook(data):
    """Função centralizada para processar webhooks"""
    
    # Ignora mensagens enviadas pelo próprio bot
    if data.get('message', {}).get('fromMe'):
        print("⚠️ IGNORADO - Mensagem enviada pelo bot")
        return {"status": "ignored - from me"}, 200
    
    # Extrai dados
    message_data = data.get('message', {})
    number = message_data.get('sender', '').replace('@s.whatsapp.net', '')
    message_text = message_data.get('text', '') or message_data.get('content', '')
    button_choice = message_data.get('buttonOrListid', '')
    
    print(f"\n📋 EXTRAÇÃO DE DADOS:")
    print(f"   📱 Número: '{number}'")
    print(f"   💬 Texto: '{message_text}'")
    print(f"   🔘 Botão: '{button_choice}'")
    
    if number and (message_text or button_choice):
        final_message = button_choice if button_choice else message_text
        print(f"   ✅ Mensagem final: '{final_message}'")
        print(f"\n🚀 INICIANDO PROCESSAMENTO...")
        
        processar_mensagem(number, final_message)
        return {"status": "success"}, 200
    
    print("❌ ERRO - Dados incompletos")
    print(f"   Número válido? {bool(number)}")
    print(f"   Mensagem válida? {bool(message_text or button_choice)}")
    return {"error": "Dados incompletos"}, 400

# ==================== ROTAS ====================

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe mensagens via webhook - rota principal"""
    try:
        data = request.json
        
        print("\n" + "="*60)
        print(f"📨 WEBHOOK RECEBIDO em {datetime.now()}")
        print(f"🔗 ROTA: /webhook")
        print("="*60)
        
        result, status_code = processar_webhook(data)
        return jsonify(result), status_code
    
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/text', methods=['POST'])
def webhook_text():
    """Recebe mensagens via webhook - rota alternativa /text"""
    try:
        data = request.json
        
        print("\n" + "="*60)
        print(f"📨 WEBHOOK RECEBIDO em {datetime.now()}")
        print(f"🔗 ROTA: /webhook/text")
        print("="*60)
        
        result, status_code = processar_webhook(data)
        return jsonify(result), status_code
    
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/test/<number>', methods=['GET'])
def testar(number):
    """Testa o bot manualmente"""
    print(f"\n🧪 TESTE MANUAL iniciado para {number}")
    
    # Limpa estado anterior
    if number in user_states:
        del user_states[number]
    
    iniciar_conversa(number)
    return jsonify({
        "status": "Iniciado", 
        "number": number,
        "mensagem": "Verifique o WhatsApp!"
    })

@app.route('/test-text/<number>', methods=['GET'])
def testar_texto(number):
    """Testa envio de texto simples"""
    print(f"\n🧪 TESTE DE TEXTO SIMPLES para {number}")
    
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    print(f"📱 Número limpo: {number_clean}")
    
    result = send_text(number_clean, "🧪 **TESTE DE CONEXÃO**\n\nSe você recebeu isso, o bot está funcionando! ✅")
    
    return jsonify({
        "status": "Enviado",
        "number": number_clean,
        "result": result,
        "token_configurado": API_TOKEN != 'SEU_TOKEN_AQUI'
    })

@app.route('/reset/<number>', methods=['GET'])
def resetar_usuario(number):
    """Reseta o estado de um usuário"""
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    
    if number_clean in user_states:
        del user_states[number_clean]
        return jsonify({
            "status": "resetado",
            "number": number_clean,
            "mensagem": "Estado do usuário foi resetado. Mande uma mensagem para começar de novo."
        })
    else:
        return jsonify({
            "status": "não encontrado",
            "number": number_clean,
            "mensagem": "Usuário não tinha estado ativo."
        })

@app.route('/health', methods=['GET'])
def health():
    """Status do servidor"""
    return jsonify({
        "status": "online",
        "usuarios_ativos": len(user_states),
        "estados_usuarios": {k: v for k, v in user_states.items()},
        "api_token_configured": API_TOKEN != 'SEU_TOKEN_AQUI',
        "api_host": API_HOST,
        "rotas_disponiveis": [
            "/webhook", 
            "/webhook/text", 
            "/test/<number>", 
            "/test-text/<number>", 
            "/reset/<number>",
            "/health"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """Página inicial"""
    return jsonify({
        "bot": "99Food Chatbot",
        "status": "online",
        "versao": "2.1-final",
        "usuarios_ativos": len(user_states),
        "rotas": {
            "webhook_principal": "/webhook",
            "webhook_alternativo": "/webhook/text",
            "teste_bot": "/test/<numero>",
            "teste_envio": "/test-text/<numero>",
            "resetar_usuario": "/reset/<numero>",
            "health_check": "/health"
        },
        "configuracao": {
            "api_host": API_HOST,
            "token_ok": API_TOKEN != 'SEU_TOKEN_AQUI',
            "link_app": LINK_APP_99FOOD,
            "link_grupo": LINK_GRUPO_OFERTAS
        }
    })

# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════╗
    🤖 CHATBOT 99FOOD - UAZAPIGO V2.1 FINAL
    ╚════════════════════════════════════════╝
    
    ✅ Servidor rodando com DEBUG COMPLETO!
    
    📡 Endpoints disponíveis:
    • POST /webhook - Recebe mensagens (principal)
    • POST /webhook/text - Recebe mensagens (alternativo)
    • GET  /test/<numero> - Testa bot completo
    • GET  /test-text/<numero> - Testa apenas envio
    • GET  /reset/<numero> - Reseta estado do usuário
    • GET  /health - Status detalhado
    • GET  / - Informações do bot
    
    🔧 Token configurado: """ + ("✅ SIM" if API_TOKEN != 'SEU_TOKEN_AQUI' else "❌ NÃO - Configure API_TOKEN!") + """
    
    🌐 API Host: """ + API_HOST + """
    
    📝 Fluxo do bot:
    1. Usuário manda qualquer mensagem → Bot inicia conversa
    2. Pergunta se tem o app instalado
    3. Pergunta se já usou cupom
    4. Envia tutorial ou grupo VIP
    
    ╚════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)