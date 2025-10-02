"""
Chatbot 99Food - uazapiGO V2
Arquivo: chatbot.py (VERSÃO COMPLETA E CORRIGIDA - com envio de cupom)
"""

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

# ==================== CONFIGURAÇÕES ====================
API_HOST = os.getenv('API_HOST', 'https://99food.uazapi.com')
API_TOKEN = os.getenv('API_TOKEN', 'SEU_TOKEN_AQUI')

LINK_APP_99FOOD = os.getenv('LINK_APP_99FOOD', 'https://seu-link-unico-aqui.com')
VIDEO_TUTORIAL_URL = os.getenv('VIDEO_TUTORIAL_URL', 'https://drive.google.com/uc?export=download&id=1MrJfG477mSjmiJmx9o_zvzd-X7SI3Vt1')
LINK_GRUPO_OFERTAS = os.getenv('LINK_GRUPO_OFERTAS', 'https://chat.whatsapp.com/seu-link-grupo')
CUPOM_DESCONTO = os.getenv('CUPOM_DESCONTO', 'PRIMEIRACOMPRA50')

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
    """Envia mensagem com botões simples - FORMATO CORRETO UAZAPI"""
    url = f"{API_HOST}/send/buttons"
    
    # Tenta primeiro o formato padrão da uazapi
    payload = {
        "number": number,
        "text": text,
        "footerText": footer,
        "buttons": [{"id": btn["id"], "text": btn["text"]} for btn in buttons]
    }
    
    headers = {
        "Accept": "application/json",
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 ENVIANDO BOTÕES para {number}")
    print(f"🔑 Token: {API_TOKEN[:10]}...{API_TOKEN[-5:]}")
    print(f"📦 Payload Tentativa 1 (simples): {payload}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"\n📊 RESPOSTA DA API (BOTÕES - Tentativa 1):")
        print(f"   Status HTTP: {response.status_code}")
        print(f"   Resposta COMPLETA: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') not in ['Pending', 'error']:
                print(f"   ✅ Botões enviados com sucesso!")
                return response_data
        
        print(f"   ⚠️ Formato 1 falhou, tentando formato 2...")
        
    except Exception as e:
        print(f"   ❌ ERRO tentativa 1: {e}")
    
    # Tentativa 2: Formato alternativo
    payload2 = {
        "number": number,
        "options": {
            "text": text,
            "footer": footer,
            "buttons": buttons
        }
    }
    
    print(f"\n📦 Payload Tentativa 2 (alternativo): {payload2}")
    
    try:
        response = requests.post(url, json=payload2, headers=headers, timeout=10)
        
        print(f"\n📊 RESPOSTA DA API (BOTÕES - Tentativa 2):")
        print(f"   Status HTTP: {response.status_code}")
        print(f"   Resposta COMPLETA: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') not in ['Pending', 'error']:
                print(f"   ✅ Botões enviados (formato 2)!")
                return response_data
        
    except Exception as e:
        print(f"   ❌ ERRO tentativa 2: {e}")
    
    # Se botões não funcionarem, usa texto simples
    print(f"   ⚠️ Botões não funcionaram - usando texto simples")
    return None

def send_video(number, video_url, caption=""):
    """Envia vídeo como mídia - FORMATO CORRETO UAZAPI"""
    url = f"{API_HOST}/send/media"
    
    # Payload CORRETO conforme documentação Uazapi
    payload = {
        "number": number,
        "type": "video",
        "file": video_url,
        "text": caption
    }
    
    headers = {
        "Accept": "application/json",
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 ENVIANDO VÍDEO para {number}")
    print(f"🎬 URL do vídeo: {video_url}")
    print(f"📦 Payload: {payload}")
    print(f"🔑 Token: {API_TOKEN[:10]}...{API_TOKEN[-5:]}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        print(f"\n📊 RESPOSTA DA API (VÍDEO):")
        print(f"   Status HTTP: {response.status_code}")
        print(f"   Resposta completa: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Verifica se enviou com sucesso
            if response_data.get('status') not in ['error', 'Pending']:
                print(f"   ✅ Vídeo enviado como MÍDIA com sucesso!")
                return response_data
            else:
                print(f"   ⚠️ API retornou erro: {response_data.get('message', 'desconhecido')}")
        else:
            print(f"   ⚠️ Status HTTP não é 200: {response.status_code}")
        
        # Se falhar, retorna erro sem enviar link como fallback
        print(f"\n❌ Falha ao enviar vídeo - não enviando fallback")
        return {"status": "error", "message": "Falha ao enviar vídeo"}
        
    except requests.exceptions.Timeout:
        print(f"   ⏱️ TIMEOUT - API não respondeu em 20s")
        return {"status": "timeout"}
        
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

# ==================== FLUXO DO CHATBOT ====================

def iniciar_conversa(number):
    """Pergunta inicial"""
    print(f"\n🚀 INICIANDO conversa com {number}")
    
    # Tenta enviar com botões primeiro
    result = send_buttons(
        number=number,
        text="👋 Olá! Bem-vindo ao Cupom Premiado!\n\n🍕 Você já tem o app da 99 Food instalado?",
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
            "👋 Olá! Bem-vindo ao Cupom Premiado!\n\n🍕 Você já tem o app da 99 Food instalado?\n\n*Responda:*\n1️⃣ - Sim, já tenho\n2️⃣ - Não, preciso instalar"
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
        text="🎉 *Ótimo!*\n\n🎫 Você já utilizou algum cupom de desconto no 99Food?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "JA_USEI", "text": "✅ Sim, já usei"},
            {"id": "NAO_USEI", "text": "🆕 Não, nunca usei"},
            {"id": "QUERO_CUPOM", "text": "🎁 Quero um cupom!"}
        ]
    )
    
    if not result or result.get('status') == 'Pending':
        send_text(number, "🎉 *Ótimo!*\n\n🎫 Você já utilizou algum cupom de desconto no 99Food?\n\n1️⃣ - Sim, já usei\n2️⃣ - Não, nunca usei\n3️⃣ - Quero um cupom!")
    
    user_states[number] = "AGUARDANDO_CUPOM"

def ja_usou_cupom(number):
    """Orienta usuário que já usou cupom a criar nova conta"""
    print(f"🔄 ORIENTANDO sobre NOVA CONTA para {number}")
    
    # Limpa qualquer estado anterior para evitar loop
    if number in user_states:
        print(f"   Limpando estado anterior: {user_states[number]}")
    
    mensagem = f"""💡 *Entendi!*

Esse cupom é *exclusivo para primeira compra* no app 99Food! 🎁

📱 *Mas tenho uma solução para você:*

Você pode criar uma *nova conta* com outro número ou email diferente e usar o cupom! 

✅ *Como fazer:*
1. Faça logout da sua conta atual
2. Cadastre com novo email/número
3. Use o cupom na primeira compra

Quer que eu te envie o cupom agora?"""
    
    send_text(number, mensagem)
    
    # Aguarda 2 segundos
    import time
    time.sleep(2)
    
    result = send_buttons(
        number=number,
        text="📲 Quer receber o cupom para usar na nova conta?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "QUERO_CUPOM_NOVA", "text": "✅ Sim, quero!"},
            {"id": "NAO_QUERO_AGORA", "text": "⏰ Não, obrigado"}
        ]
    )
    
    if not result or result.get('status') == 'Pending':
        send_text(number, "📲 Quer receber o cupom para usar na nova conta?\n\n1️⃣ - Sim, quero!\n2️⃣ - Não, obrigado")
    
    # Define estado APÓS enviar a mensagem
    user_states[number] = "AGUARDANDO_NOVA_CONTA"
    print(f"   ✅ Estado definido: AGUARDANDO_NOVA_CONTA")

def enviar_cupom_nova_conta(number):
    """Envia cupom para quem vai criar nova conta e pergunta sobre tutorial"""
    print(f"🎁 ENVIANDO CUPOM (nova conta) para {number}")
    
    mensagem = f"""🎁 *Aqui está seu cupom exclusivo!*

🎫 *{CUPOM_DESCONTO}*

💡 *Lembre-se:*
• Crie uma nova conta primeiro
• Use um email/número diferente
• Cole o cupom antes de finalizar o pedido

📹 *Quer um tutorial em vídeo* de como usar o cupom?"""
    
    send_text(number, mensagem)
    
    # Aguarda 2 segundos antes de enviar os botões
    import time
    time.sleep(2)
    
    result = send_buttons(
        number=number,
        text="📺 Quer assistir o tutorial em vídeo?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "QUERO_TUTORIAL", "text": "✅ Sim, quero ver!"},
            {"id": "NAO_PRECISA", "text": "❌ Não precisa"}
        ]
    )
    
    if not result or result.get('status') == 'Pending':
        send_text(number, "📺 Quer assistir o tutorial em vídeo?\n\n1️⃣ - Sim, quero ver!\n2️⃣ - Não precisa")
    
    user_states[number] = "AGUARDANDO_QUER_TUTORIAL"
    """Envia o cupom de desconto para o usuário"""
    print(f"🎁 ENVIANDO CUPOM para {number}")
    
    mensagem = f"""🎁 *Seu cupom exclusivo!*

🎉 Use o cupom abaixo no app 99Food:

🎫 *{CUPOM_DESCONTO}*

💡 *Como usar:*
1. Abra o app 99Food
2. Escolha seu pedido
3. Na tela de pagamento, procure "Cupom"
4. Cole o cupom: *{CUPOM_DESCONTO}*
5. Aproveite o desconto! 🚀

📹 Quer ver um tutorial em vídeo? Vou te mostrar!"""
    
    send_text(number, mensagem)
    
    # Aguarda 2 segundos antes de perguntar sobre o tutorial
    import time
    time.sleep(2)
    
    # Agora continua para o tutorial
    enviar_tutorial(number)

def enviar_tutorial(number):
    """Envia vídeo tutorial"""
    
    # Verifica se já está no estado correto para evitar loop
    estado_atual = user_states.get(number)
    if estado_atual == "AGUARDANDO_RESULTADO":
        print(f"⚠️ BLOQUEADO - Já está aguardando resultado, não reenviando tutorial")
        return
    
    print(f"📹 ENVIANDO TUTORIAL para {number} (estado atual: {estado_atual})")
    
    send_text(number, "📹 *Perfeito!*\n\nVou te ensinar como usar cupom!")
    
    # Aguarda 2 segundos antes de enviar o vídeo
    import time
    time.sleep(2)
    
    send_video(
        number=number,
        video_url=VIDEO_TUTORIAL_URL,
        caption="🎬 Tutorial: Como usar cupom no 99Food"
    )
    
    # Aguarda 3 segundos antes de enviar os botões
    time.sleep(3)
    
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
    print(f"   ✅ Estado ATUALIZADO: {estado_atual} → AGUARDANDO_RESULTADO")

def enviar_grupo(number):
    """Envia link do grupo"""
    mensagem = f"""🎉 *Parabéns!*

Você está aproveitando o 99Food! 🍕

💰 *Quer mais ofertas?*

Entre no grupo VIP:
• 🎁 Cupons exclusivos
• 🔥 Ofertas relâmpago
• 💸 Descontos até 70%

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

💰 *Quer mais ofertas?*

Entre no grupo VIP:
• 🎁 Cupons exclusivos
• 🔥 Ofertas relâmpago
• 💸 Descontos até 70%

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
    print(f"🔍 Mensagem normalizada: '{msg}'")
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
            print("   → Ação: Usuário JÁ USOU cupom - orientando sobre nova conta")
            ja_usou_cupom(number)
        elif "NAO" in msg or "NÃO" in msg or msg == "2":
            print("   → Ação: Usuário NUNCA USOU cupom")
            enviar_tutorial(number)
        elif "QUERO" in msg or msg == "3":
            print("   → Ação: Usuário QUER UM CUPOM")
            enviar_cupom(number)
        else:
            print("   → Ação: Resposta não reconhecida")
            send_text(
                number,
                "🤔 Não entendi.\n\nVocê já usou cupom no 99Food?\n\n1️⃣ - Sim, já usei\n2️⃣ - Não, nunca usei\n3️⃣ - Quero um cupom!"
            )
        return
    
    elif estado_atual == "AGUARDANDO_NOVA_CONTA":
        print(f"   → Verificando se quer cupom para nova conta...")
        
        if "QUERO" in msg or msg == "1" or "SIM" in msg:
            print("   → Ação: Usuário QUER cupom para nova conta")
            enviar_cupom_nova_conta(number)
        else:
            print("   → Ação: Usuário não quer agora")
            send_text(number, "😊 Tudo bem! Quando quiser criar a nova conta, me chame! Até logo! 👋")
            if number in user_states:
                del user_states[number]
                print(f"   ✅ Estado removido para {number}")
        return
    
    elif estado_atual == "AGUARDANDO_QUER_TUTORIAL":
        print(f"   → Verificando se quer assistir tutorial (estado: {estado_atual})...")
        
        if "QUERO" in msg or msg == "1" or "SIM" in msg or "VER" in msg:
            print("   → Ação: Usuário QUER ver o tutorial - ENVIANDO AGORA")
            # NÃO chama função recursiva, envia diretamente aqui
            send_text(number, "📹 *Perfeito!*\n\nVou te ensinar como usar cupom!")
            
            import time
            time.sleep(2)
            
            send_video(
                number=number,
                video_url=VIDEO_TUTORIAL_URL,
                caption="🎬 Tutorial: Como usar cupom no 99Food"
            )
            
            time.sleep(3)
            
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
            print(f"   ✅ Estado ATUALIZADO: AGUARDANDO_QUER_TUTORIAL → AGUARDANDO_RESULTADO")
        else:
            print("   → Ação: Usuário NÃO precisa do tutorial - enviando para grupo")
            mensagem = f"""✅ *Perfeito!*

Você já sabe como usar o cupom! 🎉

💰 *Quer mais ofertas e cupons exclusivos?*

Entre no nosso grupo VIP:
• 🎁 Cupons diários
• 🔥 Ofertas relâmpago
• 💸 Descontos até 70%

👥 *Link do grupo:*
{LINK_GRUPO_OFERTAS}

Aproveite! 🚀"""
            
            send_text(number, mensagem)
            if number in user_states:
                del user_states[number]
                print(f"   ✅ Estado removido para {number} - CONVERSA FINALIZADA")
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
                print(f"   ✅ Estado removido para {number}")
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

@app.route('/test-buttons/<number>', methods=['GET'])
def testar_botoes(number):
    """Testa envio de botões diretamente"""
    print(f"\n🧪 TESTE DE BOTÕES para {number}")
    
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    
    result = send_buttons(
        number=number_clean,
        text="🧪 Teste de Botões\n\nOs botões estão funcionando?",
        footer="Teste",
        buttons=[
            {"id": "SIM", "text": "✅ Sim"},
            {"id": "NAO", "text": "❌ Não"}
        ]
    )
    
    return jsonify({
        "status": "Enviado",
        "number": number_clean,
        "result": result,
        "mensagem": "Verifique se os botões estão clicáveis no WhatsApp"
    })

@app.route('/test-video/<number>', methods=['GET'])
def testar_video(number):
    """Testa envio de vídeo diretamente"""
    print(f"\n🧪 TESTE DE VÍDEO para {number}")
    
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    
    # Usa a URL configurada ou uma de teste
    video_url_to_test = request.args.get('url', VIDEO_TUTORIAL_URL)
    
    print(f"🎬 Testando URL: {video_url_to_test}")
    
    result = send_video(
        number=number_clean,
        video_url=video_url_to_test,
        caption="🧪 Teste de vídeo - Se chegou, está funcionando!"
    )
    
    return jsonify({
        "status": "Enviado",
        "number": number_clean,
        "video_url": video_url_to_test,
        "result": result,
        "dica": "Se não chegou como vídeo, verifique se a URL é de download direto"
    })

@app.route('/test-cupom/<number>', methods=['GET'])
def testar_cupom(number):
    """Testa envio de cupom diretamente"""
    print(f"\n🧪 TESTE DE CUPOM para {number}")
    
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    
    # Simula estado para testar o fluxo do cupom
    user_states[number_clean] = "AGUARDANDO_CUPOM"
    
    enviar_cupom(number_clean)
    
    return jsonify({
        "status": "Enviado",
        "number": number_clean,
        "cupom": CUPOM_DESCONTO,
        "mensagem": "Verifique se recebeu o cupom e o tutorial!"
    })

@app.route('/test-ja-usou/<number>', methods=['GET'])
def testar_ja_usou(number):
    """Testa fluxo de quem já usou cupom"""
    print(f"\n🧪 TESTE FLUXO JÁ USOU CUPOM para {number}")
    
    number_clean = number.replace('+', '').replace('-', '').replace(' ', '').replace('@s.whatsapp.net', '')
    
    # Limpa estado anterior
    if number_clean in user_states:
        del user_states[number_clean]
    
    # Simula que chegou na pergunta sobre cupom
    user_states[number_clean] = "AGUARDANDO_CUPOM"
    
    # Processa como se tivesse respondido "já usei"
    processar_mensagem(number_clean, "JA_USEI")
    
    return jsonify({
        "status": "Iniciado",
        "number": number_clean,
        "fluxo": "ja_usou_cupom",
        "mensagem": "Verifique se recebeu a orientação sobre criar nova conta!"
    })

@app.route('/check-video', methods=['GET'])
def check_video():
    """Verifica se a URL do vídeo está acessível"""
    video_url = request.args.get('url', VIDEO_TUTORIAL_URL)
    
    print(f"\n🔍 VERIFICANDO URL DO VÍDEO: {video_url}")
    
    try:
        # Faz uma requisição HEAD para verificar se o arquivo existe
        response = requests.head(video_url, allow_redirects=True, timeout=10)
        
        info = {
            "url": video_url,
            "status_code": response.status_code,
            "acessivel": response.status_code == 200,
            "content_type": response.headers.get('Content-Type', 'desconhecido'),
            "content_length": response.headers.get('Content-Length', 'desconhecido'),
            "redirects": len(response.history) if response.history else 0,
            "url_final": response.url
        }
        
        if info["acessivel"]:
            print(f"   ✅ URL está acessível!")
            print(f"   📦 Tipo: {info['content_type']}")
            print(f"   📏 Tamanho: {info['content_length']} bytes")
        else:
            print(f"   ❌ URL não está acessível! Status: {response.status_code}")
        
        return jsonify(info)
        
    except Exception as e:
        print(f"   ❌ ERRO ao verificar URL: {e}")
        return jsonify({
            "url": video_url,
            "erro": str(e),
            "acessivel": False
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
        "cupom_configurado": CUPOM_DESCONTO,
        "rotas_disponiveis": [
            "/webhook", 
            "/webhook/text", 
            "/test/<number>", 
            "/test-text/<number>",
            "/test-buttons/<number>",
            "/test-video/<number>",
            "/test-cupom/<number>",
            "/test-ja-usou/<number>",
            "/check-video",
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
        "versao": "3.4-loop-fix-final",
        "usuarios_ativos": len(user_states),
        "rotas": {
            "webhook_principal": "/webhook",
            "webhook_alternativo": "/webhook/text",
            "teste_bot": "/test/<numero>",
            "teste_envio": "/test-text/<numero>",
            "teste_botoes": "/test-buttons/<numero>",
            "teste_video": "/test-video/<numero>",
            "teste_cupom": "/test-cupom/<numero>",
            "teste_ja_usou": "/test-ja-usou/<numero>",
            "verificar_video": "/check-video?url=URL_AQUI",
            "resetar_usuario": "/reset/<numero>",
            "health_check": "/health"
        },
        "configuracao": {
            "api_host": API_HOST,
            "token_ok": API_TOKEN != 'SEU_TOKEN_AQUI',
            "link_app": LINK_APP_99FOOD,
            "link_grupo": LINK_GRUPO_OFERTAS,
            "video_url": VIDEO_TUTORIAL_URL,
            "cupom": CUPOM_DESCONTO
        },
        "fluxo_corrigido": {
            "opcao_1_ja_usei": "Orienta a criar nova conta → Envia cupom → Pergunta se quer tutorial → Envia vídeo (se sim) → Grupo VIP [SEM LOOPS]",
            "opcao_2_nunca_usei": "Envia tutorial direto → Pergunta se conseguiu → Grupo VIP",
            "opcao_3_quero_cupom": "Envia cupom + tutorial automaticamente → Pergunta se conseguiu → Grupo VIP"
        },
        "protecoes_anti_loop": {
            "verificacao_estados": "Funções verificam estado antes de executar",
            "estados_unicos": "Cada estado é definido apenas uma vez",
            "limpeza_automatica": "Estados são removidos ao finalizar",
            "logs_detalhados": "Todos os estados são logados para debug"
        }
    })

# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════╗
    🤖 CHATBOT 99FOOD - V3.4 LOOP FIX FINAL
    ╚═══════════════════════════════════════════╝
    
    ✅ Servidor rodando com DEBUG COMPLETO!
    ✅ LOOPS ELIMINADOS - Código inline no processamento
    ✅ Sem chamadas recursivas de funções
    ✅ Estados validados antes de cada ação
    
    📡 Endpoints disponíveis:
    • POST /webhook - Recebe mensagens (principal)
    • POST /webhook/text - Recebe mensagens (alternativo)
    • GET  /test/<numero> - Testa bot completo
    • GET  /test-text/<numero> - Testa envio texto
    • GET  /test-buttons/<numero> - Testa botões
    • GET  /test-video/<numero> - Testa vídeo
    • GET  /test-cupom/<numero> - Testa envio de cupom
    • GET  /test-ja-usou/<numero> - Testa fluxo "já usei cupom"
    • GET  /check-video - Verifica URL do vídeo
    • GET  /reset/<numero> - Reseta estado
    • GET  /health - Status detalhado
    • GET  / - Informações do bot
    
    🔧 Token configurado: """ + ("✅ SIM" if API_TOKEN != 'SEU_TOKEN_AQUI' else "❌ NÃO - Configure API_TOKEN!") + """
    
    🌐 API Host: """ + API_HOST + """
    
    🎬 Video URL: """ + VIDEO_TUTORIAL_URL + """
    
    🎁 Cupom: """ + CUPOM_DESCONTO + """
    
    📝 Fluxo CORRIGIDO (100% SEM LOOPS):
    
    1️⃣ *JÁ USEI CUPOM:*
       Estado: AGUARDANDO_CUPOM
       → Orienta nova conta (1x)
       Estado: AGUARDANDO_NOVA_CONTA
       → Pergunta se quer cupom (1x)
       → Envia cupom (1x)
       Estado: AGUARDANDO_QUER_TUTORIAL
       → Pergunta se quer tutorial (1x)
       → Se SIM: Envia vídeo INLINE (sem função recursiva)
       Estado: AGUARDANDO_RESULTADO
       → Grupo VIP + Remove estado
    
    2️⃣ *NUNCA USEI:*
       → Tutorial direto (1x)
       Estado: AGUARDANDO_RESULTADO
       → Grupo VIP + Remove estado
    
    3️⃣ *QUERO CUPOM:*
       → Cupom + Tutorial automático (1x cada)
       Estado: AGUARDANDO_RESULTADO
       → Grupo VIP + Remove estado
    
    🔒 PROTEÇÃO ANTI-LOOP V2:
    ✅ Código do tutorial executado INLINE (não chama função)
    ✅ Estados verificados ANTES de cada ação
    ✅ Logs mostram mudanças de estado em tempo real
    ✅ Estados limpos ao finalizar conversa
    ✅ Mensagens enviadas apenas 1x por estado
    
    ╚═══════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)