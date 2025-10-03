# -*- coding: utf-8 -*-
"""
Chatbot 99Food - uazapiGO V4.1
Arquivo: chatbot.py
Versao: 4.1 - Com persistencia de dados e mensagens formatadas
"""

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os
import time
import json

# ==================== CONFIGURACOES ====================
API_HOST = os.getenv('API_HOST', 'https://99food.uazapi.com')
API_TOKEN = os.getenv('API_TOKEN', 'SEU_TOKEN_AQUI')

LINK_APP_99FOOD = os.getenv('LINK_APP_99FOOD', 'https://seu-link-unico-aqui.com')
VIDEO_TUTORIAL_URL = os.getenv('VIDEO_TUTORIAL_URL', 'https://drive.google.com/uc?export=download&id=1MrJfG477mSjmiJmx9o_zvzd-X7SI3Vt1')
LINK_GRUPO_OFERTAS = os.getenv('LINK_GRUPO_OFERTAS', 'https://chat.whatsapp.com/seu-link-grupo')
CUPOM_DESCONTO = os.getenv('CUPOM_DESCONTO', 'PRIMEIRACOMPRA50')

PORT = int(os.getenv('PORT', 5000))

app = Flask(__name__)
user_states = {}

# ==================== SISTEMA DE ESTATISTICAS ====================
STATS_FILE = 'bot_estatisticas.json'

def carregar_estatisticas():
    """Carrega estatisticas do arquivo"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                print(f"Estatisticas carregadas: {stats.get('total_conversas', 0)} conversas totais")
                return stats
    except Exception as e:
        print(f"Erro ao carregar estatisticas: {e}")
    
    return {
        "total_conversas": 0,
        "conversas_hoje": [],
        "conversas_finalizadas": 0,
        "cupons_enviados": 0,
        "tutoriais_enviados": 0,
        "usuarios_grupo": 0,
        "usuarios_por_data": {}
    }

def salvar_estatisticas():
    """Salva estatisticas no arquivo"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(estatisticas, f, ensure_ascii=False, indent=2)
        print(f"Estatisticas salvas: {estatisticas['total_conversas']} conversas totais")
    except Exception as e:
        print(f"Erro ao salvar estatisticas: {e}")

estatisticas = carregar_estatisticas()

COMANDO_RELATORIO = os.getenv('COMANDO_RELATORIO', 'admin/relatorio')

def registrar_estatistica(tipo, numero):
    """Registra estatisticas de uso do bot"""
    from datetime import date
    
    hoje = str(date.today())
    
    if tipo == "nova_conversa":
        estatisticas["total_conversas"] += 1
        if numero not in estatisticas["conversas_hoje"]:
            estatisticas["conversas_hoje"].append(numero)
        
        if hoje not in estatisticas["usuarios_por_data"]:
            estatisticas["usuarios_por_data"][hoje] = []
        if numero not in estatisticas["usuarios_por_data"][hoje]:
            estatisticas["usuarios_por_data"][hoje].append(numero)
    
    elif tipo == "conversa_finalizada":
        estatisticas["conversas_finalizadas"] += 1
    
    elif tipo == "cupom_enviado":
        estatisticas["cupons_enviados"] += 1
    
    elif tipo == "tutorial_enviado":
        estatisticas["tutoriais_enviados"] += 1
    
    elif tipo == "grupo_enviado":
        estatisticas["usuarios_grupo"] += 1
    
    salvar_estatisticas()

def gerar_relatorio():
    """Gera relatorio formatado das estatisticas com numeros completos"""
    from datetime import date
    
    hoje = str(date.today())
    usuarios_hoje = len(estatisticas["conversas_hoje"])
    
    relatorio = f"""RELATORIO DO BOT 99FOOD

Data: {hoje}

USUARIOS HOJE:
Total de contatos: {usuarios_hoje}

ESTATISTICAS GERAIS:
Total de conversas: {estatisticas['total_conversas']}
Conversas finalizadas: {estatisticas['conversas_finalizadas']}
Cupons enviados: {estatisticas['cupons_enviados']}
Tutoriais enviados: {estatisticas['tutoriais_enviados']}
Usuarios que entraram no grupo: {estatisticas['usuarios_grupo']}

USUARIOS ATIVOS AGORA:
Em conversa: {len(user_states)}

NUMEROS DE HOJE:"""
    
    if usuarios_hoje > 0:
        for idx, numero in enumerate(estatisticas["conversas_hoje"], 1):
            relatorio += f"\n{idx}. {numero}"
    else:
        relatorio += "\nNenhum usuario hoje ainda."
    
    relatorio += f"\n\nRelatorio gerado com sucesso!"
    
    return relatorio

# ==================== FUNCOES DE ENVIO ====================

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
    
    print(f"\nENVIANDO TEXTO para {number}")
    print(f"Mensagem: {text[:100]}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status HTTP: {response.status_code}")
        
        try:
            response_data = response.json()
            return response_data
        except:
            print(f"Erro ao parsear JSON da resposta")
            return {"status": "error", "raw": response.text}
            
    except requests.exceptions.Timeout:
        print(f"TIMEOUT - API nao respondeu em 10s")
        return None
    except Exception as e:
        print(f"EXCECAO: {e}")
        return None

def send_buttons(number, text, footer, buttons):
    """Envia mensagem com botoes"""
    url = f"{API_HOST}/send/buttons"
    
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
    
    print(f"\nENVIANDO BOTOES para {number}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') not in ['Pending', 'error']:
                print(f"Botoes enviados com sucesso!")
                return response_data
        
        print(f"Formato 1 falhou, tentando formato 2...")
        
    except Exception as e:
        print(f"Erro tentativa 1: {e}")
    
    payload2 = {
        "number": number,
        "options": {
            "text": text,
            "footer": footer,
            "buttons": buttons
        }
    }
    
    try:
        response = requests.post(url, json=payload2, headers=headers, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') not in ['Pending', 'error']:
                print(f"Botoes enviados (formato 2)!")
                return response_data
        
    except Exception as e:
        print(f"Erro tentativa 2: {e}")
    
    print(f"Botoes nao funcionaram - retornando None")
    return None

def send_video(number, video_url, caption=""):
    """Envia video como midia"""
    url = f"{API_HOST}/send/media"
    
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
    
    print(f"\nENVIANDO VIDEO para {number}")
    print(f"URL do video: {video_url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('status') not in ['error', 'Pending']:
                print(f"Video enviado como MIDIA com sucesso!")
                return response_data
        
        print(f"\nFalha ao enviar video")
        return {"status": "error", "message": "Falha ao enviar video"}
        
    except requests.exceptions.Timeout:
        print(f"TIMEOUT - API nao respondeu em 20s")
        return {"status": "timeout"}
        
    except Exception as e:
        print(f"EXCECAO: {e}")
        return {"status": "error", "error": str(e)}

# ==================== FLUXO DO CHATBOT ====================

def iniciar_conversa(number):
    """Pergunta inicial"""
    print(f"\nINICIANDO conversa com {number}")
    
    registrar_estatistica("nova_conversa", number)
    
    result = send_buttons(
        number=number,
        text="👋 Olá! Bem-vindo ao Cupom Premiado! Vamos te ajudar a resgatar o seu cupom de 70% de desconto!\n\n🍕 Você já tem o app da 99 Food instalado?",
        footer="Chatbot 99Food",
        buttons=[
            {"id": "SIM", "text": "✅ Sim, já tenho"},
            {"id": "NAO", "text": "📲 Não, preciso instalar"}
        ]
    )
    
    if not result or result.get('status') == 'Pending':
        print("Botoes falharam, enviando texto simples...")
        send_text(
            number,
            "👋 Olá! Bem-vindo ao Cupom Premiado!\n\nResponda apenas com números\n\n🍕 Você já tem o app da 99 Food instalado?\n\n*Responda:*\n1️⃣ - Sim, já tenho\n2️⃣ - Não, preciso instalar"
        )
    
    user_states[number] = "AGUARDANDO_TEM_APP"
    print(f"Estado definido: AGUARDANDO_TEM_APP")

def nao_tem_app(number):
    """Envia link para download"""
    mensagem = f"""📲 *Sem problemas!*

Baixe o app da 99Food agora:

🔗 *Link do app:*
{LINK_APP_99FOOD}

Após instalar, volte aqui! 😊"""
    
    send_text(number, mensagem)
    
    time.sleep(2)
    
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
    print(f"Estado definido: AGUARDANDO_INSTALACAO")

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
    print(f"Estado definido: AGUARDANDO_CUPOM")

def ja_usou_cupom(number):
    """Orienta sobre nova conta"""
    print(f"ORIENTANDO sobre NOVA CONTA para {number}")
    
    mensagem = f"""💡 *Entendi!*

Esse cupom é *exclusivo para primeira compra* no app 99Food! 🎁

📱 *Mas tenho uma solução para você:*

Você pode criar uma *nova conta* com outro número ou email diferente e usar o cupom! 

✅ *Como fazer:*
1. Faça logout da sua conta atual
2. Cadastre com novo email/número
3. Use o cupom na primeira compra

💬 *Digite qualquer coisa quando estiver pronto para receber o cupom!* 👇"""
    
    send_text(number, mensagem)
    
    user_states[number] = "AGUARDANDO_CONFIRMACAO_NOVA_CONTA"
    print(f"Estado definido: AGUARDANDO_CONFIRMACAO_NOVA_CONTA")

def enviar_cupom_e_aguardar(number):
    """Envia cupom e aguarda confirmacao para o tutorial"""
    print(f"ENVIANDO CUPOM para {number}")
    
    registrar_estatistica("cupom_enviado", number)
    
    mensagem = f"""🎁 *Aqui está seu cupom exclusivo!*

🎫 *{CUPOM_DESCONTO}*

Para ter acesso a outras ofertas, entre no nosso grupo VIP!
chat.whatsapp.com/CoQl7hC1PFm90IEiBHEj94

💡 *Como usar:*
1. Abra o app 99Food
2. Escolha seu pedido
3. Na tela de pagamento, procure "Cupom"
4. Cole o cupom: *{CUPOM_DESCONTO}*
5. Aproveite o desconto! 🚀

🎹 *Quer ver um tutorial em vídeo de como usar?*

💬 *Digite qualquer coisa para ver o tutorial!* 👇"""
    
    send_text(number, mensagem)
    
    user_states[number] = "AGUARDANDO_CONFIRMACAO_TUTORIAL"
    print(f"Estado definido: AGUARDANDO_CONFIRMACAO_TUTORIAL")

def enviar_tutorial_e_aguardar(number):
    """Envia tutorial e aguarda resultado"""
    print(f"ENVIANDO TUTORIAL para {number}")
    
    registrar_estatistica("tutorial_enviado", number)
    
    send_text(number, "🎹 *Perfeito!*\n\nVou te mostrar como usar o cupom!")
    
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
        send_text(number, "📺 Conseguiu usar o cupom?\n\n1️⃣ - Sim, consegui!\n2️⃣ - Não consegui\n3️⃣ - Vou tentar depois")
    
    user_states[number] = "AGUARDANDO_RESULTADO"
    print(f"Estado definido: AGUARDANDO_RESULTADO")

def enviar_grupo_final(number):
    """Envia link do grupo e finaliza"""
    
    registrar_estatistica("grupo_enviado", number)
    registrar_estatistica("conversa_finalizada", number)
    
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
        print(f"CONVERSA FINALIZADA - Estado removido para {number}")

def nao_deu_certo_tutorial(number):
    """Dificuldade apos tutorial"""
    mensagem = """😔 Que pena!

📞 *Vamos te ajudar:*

1️⃣ Assista novamente o vídeo
2️⃣ Copie o cupom corretamente
3️⃣ Cole antes de finalizar o pedido

💬 *Me mande mensagem se precisar de ajuda!* 😊"""
    
    send_text(number, mensagem)
    
    if number in user_states:
        del user_states[number]
        print(f"Estado removido para {number}")

# ==================== PROCESSAMENTO ====================

def verificar_pergunta_cupom(message):
    """Verifica se a mensagem e uma pergunta sobre o cupom"""
    msg = message.upper().strip()
    
    # Detecta qualquer mensagem que contenha a palavra CUPOM
    if "CUPOM" in msg:
        return True
    
    return False

def responder_cupom_direto(number):
    """Responde diretamente com o cupom quando perguntado"""
    print(f"RESPONDENDO CUPOM DIRETO para {number}")
    
    registrar_estatistica("cupom_enviado", number)
    
    mensagem = f"""🎁 *Seu cupom exclusivo:*

🎫 *{CUPOM_DESCONTO}*

💡 *Como usar:*
1. Abra o app 99Food
2. Escolha seu pedido
3. Na tela de pagamento, procure "Cupom"
4. Cole o cupom: *{CUPOM_DESCONTO}*
5. Aproveite o desconto! 🚀

🎹 *Precisa de ajuda?* Digite qualquer coisa e te envio um tutorial em vídeo!"""
    
    send_text(number, mensagem)
    
    user_states[number] = "AGUARDANDO_CONFIRMACAO_TUTORIAL"
    print(f"Estado definido: AGUARDANDO_CONFIRMACAO_TUTORIAL")

def processar_mensagem(number, message):
    """Processa mensagens e gerencia fluxo"""
    
    estado_atual = user_states.get(number, "INICIO")
    msg = message.upper().strip()
    
    print(f"\n{'='*60}")
    print(f"PROCESSANDO MENSAGEM")
    print(f"Usuario: {number}")
    print(f"Estado atual: {estado_atual}")
    print(f"Mensagem recebida: '{message}'")
    print(f"{'='*60}")
    
    if msg.strip() == COMANDO_RELATORIO.upper():
        print("DETECTADO: Comando de relatorio!")
        relatorio = gerar_relatorio()
        send_text(number, relatorio)
        return
    
    if verificar_pergunta_cupom(message):
        print("DETECTADO: Pergunta sobre cupom!")
        responder_cupom_direto(number)
        return
    
    if estado_atual == "INICIO" or number not in user_states:
        print("Acao: Iniciar conversa (primeiro contato)")
        iniciar_conversa(number)
        return
    
    elif estado_atual == "AGUARDANDO_TEM_APP":
        print(f"Verificando resposta sobre ter app...")
        
        if "SIM" in msg or msg == "1":
            print("Acao: Usuario TEM o app")
            tem_app(number)
        elif "NAO" in msg or msg == "2":
            print("Acao: Usuario NAO TEM o app")
            nao_tem_app(number)
        else:
            print("Acao: Resposta nao reconhecida, repetindo pergunta")
            send_text(
                number,
                "🤔 Não entendi sua resposta.\n\nPor favor, escolha uma opção:\n\n1️⃣ - Sim, já tenho o app\n2️⃣ - Não, preciso instalar"
            )
        return
    
    elif estado_atual == "AGUARDANDO_INSTALACAO":
        print(f"Verificando instalacao...")
        
        if "INSTALOU" in msg or msg == "1" or "SIM" in msg:
            print("Acao: Usuario INSTALOU o app")
            tem_app(number)
        else:
            print("Acao: Usuario vai instalar depois")
            send_text(number, "😊 Ok! Quando instalar, me mande uma mensagem! Até logo! 👋")
            if number in user_states:
                del user_states[number]
                print(f"Estado removido para {number}")
        return
    
    elif estado_atual == "AGUARDANDO_CUPOM":
        print(f"Verificando uso de cupom...")
        
        if "JA" in msg or msg == "1":
            print("Acao: Usuario JA USOU cupom - orientando sobre nova conta")
            ja_usou_cupom(number)
        elif "NAO" in msg or msg == "2":
            print("Acao: Usuario NUNCA USOU cupom - enviando cupom")
            enviar_cupom_e_aguardar(number)
        elif "QUERO" in msg or msg == "3":
            print("Acao: Usuario QUER UM CUPOM - enviando cupom")
            enviar_cupom_e_aguardar(number)
        else:
            print("Acao: Resposta nao reconhecida")
            send_text(
                number,
                "🤔 Não entendi.\n\nVocê já usou cupom no 99Food?\n\n1️⃣ - Sim, já usei\n2️⃣ - Não, nunca usei\n3️⃣ - Quero um cupom!"
            )
        return
    
    elif estado_atual == "AGUARDANDO_CONFIRMACAO_NOVA_CONTA":
        print(f"Usuario CONFIRMOU que vai criar nova conta")
        print(f"Acao: Enviando cupom agora")
        enviar_cupom_e_aguardar(number)
        return
    
    elif estado_atual == "AGUARDANDO_CONFIRMACAO_TUTORIAL":
        print(f"Usuario QUER o tutorial")
        print(f"Acao: Enviando tutorial agora")
        enviar_tutorial_e_aguardar(number)
        return
    
    elif estado_atual == "AGUARDANDO_RESULTADO":
        print(f"Verificando resultado do tutorial...")
        
        if "DEU_CERTO" in msg or msg == "1" or "CONSEGUI" in msg or "SIM" in msg:
            print("Acao: Tutorial DEU CERTO - enviando grupo")
            enviar_grupo_final(number)
        elif "NAO_DEU_CERTO" in msg or msg == "2" or "NAO CONSEGUI" in msg:
            print("Acao: Tutorial NAO DEU CERTO - enviando ajuda")
            nao_deu_certo_tutorial(number)
        else:
            print("Acao: Vai tentar depois")
            send_text(number, "😊 Sem pressa! Quando testar, me avise! Até logo! 👋")
            if number in user_states:
                del user_states[number]
                print(f"Estado removido para {number}")
        return
    
    else:
        print("Estado desconhecido, reiniciando conversa")
        iniciar_conversa(number)

def processar_webhook(data):
    """Funcao centralizada para processar webhooks"""
    
    if data.get('message', {}).get('fromMe'):
        print("IGNORADO - Mensagem enviada pelo bot")
        return {"status": "ignored - from me"}, 200
    
    message_data = data.get('message', {})
    number = message_data.get('sender', '').replace('@s.whatsapp.net', '')
    message_text = message_data.get('text', '') or message_data.get('content', '')
    button_choice = message_data.get('buttonOrListid', '')
    
    print(f"\nEXTRACAO DE DADOS:")
    print(f"Numero: '{number}'")
    print(f"Texto: '{message_text}'")
    print(f"Botao: '{button_choice}'")
    
    if number and (message_text or button_choice):
        final_message = button_choice if button_choice else message_text
        print(f"Mensagem final: '{final_message}'")
        print(f"\nINICIANDO PROCESSAMENTO...")
        
        processar_mensagem(number, final_message)
        return {"status": "success"}, 200
    
    print("ERRO - Dados incompletos")
    return {"error": "Dados incompletos"}, 400

# ==================== ROTAS ====================

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe mensagens via webhook - rota principal"""
    try:
        data = request.json
        
        print("\n" + "="*60)
        print(f"WEBHOOK RECEBIDO em {datetime.now()}")
        print(f"ROTA: /webhook")
        print("="*60)
        
        result, status_code = processar_webhook(data)
        return jsonify(result), status_code
    
    except Exception as e:
        print(f"\nERRO CRITICO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/text', methods=['POST'])
def webhook_text():
    """Recebe mensagens via webhook - rota alternativa /text"""
    try:
        data = request.json
        
        print("\n" + "="*60)
        print(f"WEBHOOK RECEBIDO em {datetime.now()}")
        print(f"ROTA: /webhook/text")
        print("="*60)
        
        result, status_code = processar_webhook(data)
        return jsonify(result), status_code
    
    except Exception as e:
        print(f"\nERRO CRITICO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Status do servidor"""
    return jsonify({
        "status": "online",
        "version": "4.1-integrado",
        "usuarios_ativos": len(user_states),
        "total_conversas": estatisticas["total_conversas"],
        "usuarios_hoje": len(estatisticas["conversas_hoje"])
    })

@app.route('/', methods=['GET'])
def home():
    """Pagina inicial"""
    return jsonify({
        "bot": "99Food Chatbot",
        "status": "online",
        "versao": "4.1-integrado",
        "usuarios_ativos": len(user_states),
        "total_conversas": estatisticas["total_conversas"]
    })

# ==================== EXECUCAO ====================

if __name__ == '__main__':
    print("""
    CHATBOT 99FOOD - V4.1 INTEGRADO
    
    Servidor rodando!
    Porta: """ + str(PORT) + """
    
    Estatisticas carregadas:
    Total de conversas: """ + str(estatisticas["total_conversas"]) + """
    Usuarios hoje: """ + str(len(estatisticas["conversas_hoje"])) + """
    
    Token configurado: """ + ("SIM" if API_TOKEN != 'SEU_TOKEN_AQUI' else "NAO - Configure API_TOKEN!") + """
    
    Pronto para receber mensagens!
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)