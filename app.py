import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações do Uazapi (serão definidas como variáveis de ambiente no Render)
UAZAPI_INSTANCE_ID = os.getenv('UAZAPI_INSTANCE_ID', 'YOUR_INSTANCE_ID')
UAZAPI_INSTANCE_TOKEN = os.getenv('UAZAPI_INSTANCE_TOKEN', 'YOUR_TOKEN')
UAZAPI_BASE_URL = os.getenv('UAZAPI_BASE_URL', 'https://api.uazapi.com/api')

# Links e configurações
PLAYSTORE_LINK = "https://play.google.com/store/apps/details?id=com.taxis99"
APPSTORE_LINK = "https://apps.apple.com/br/app/99-carros/id553663691"
VIDEO_TUTORIAL_URL = "https://exemplo.com/video-tutorial.mp4"  # Substitua pelo link real do vídeo
GRUPO_OFERTAS_LINK = "https://chat.whatsapp.com/XXXXXXXXX"  # Substitua pelo link real do grupo

# Armazenamento temporário de estados de conversa (em produção, use um banco de dados)
user_states = {}

class ChatbotFlow:
    STATES = {
        'INITIAL': 'initial',
        'WAITING_APP_RESPONSE': 'waiting_app_response',
        'WAITING_CUPOM_RESPONSE': 'waiting_cupom_response',
        'WAITING_TUTORIAL_FEEDBACK': 'waiting_tutorial_feedback',
        'COMPLETED': 'completed'
    }

class UazapiClient:
    def __init__(self, instance_id, token, base_url):
        self.instance_id = instance_id
        self.token = token
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    
    def send_text(self, to, message):
        """Envia mensagem de texto"""
        url = f"{self.base_url}/{self.instance_id}/messages/send"
        payload = {
            "to": to,
            "body": message,
            "type": "text"
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Mensagem enviada para {to}")
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return None
    
    def send_media(self, to, media_url, caption, media_type="video"):
        """Envia mídia (vídeo ou imagem)"""
        url = f"{self.base_url}/{self.instance_id}/messages/send"
        payload = {
            "to": to,
            "media_url": media_url,
            "caption": caption,
            "type": media_type
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Mídia enviada para {to}")
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mídia: {e}")
            return None
    
    def send_buttons(self, to, message, buttons):
        """Envia mensagem com botões"""
        url = f"{self.base_url}/{self.instance_id}/messages/send"
        payload = {
            "to": to,
            "body": message,
            "type": "buttons",
            "buttons": buttons
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Botões enviados para {to}")
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar botões: {e}")
            return None

# Inicializa cliente Uazapi
uazapi = UazapiClient(UAZAPI_INSTANCE_ID, UAZAPI_INSTANCE_TOKEN, UAZAPI_BASE_URL)

def get_user_state(user_id):
    """Obtém o estado atual do usuário"""
    return user_states.get(user_id, {
        'state': ChatbotFlow.STATES['INITIAL'],
        'data': {}
    })

def update_user_state(user_id, state, data=None):
    """Atualiza o estado do usuário"""
    if user_id not in user_states:
        user_states[user_id] = {'state': state, 'data': {}}
    else:
        user_states[user_id]['state'] = state
    
    if data:
        user_states[user_id]['data'].update(data)
    
    logger.info(f"Estado atualizado para {user_id}: {state}")

def process_message(sender, message_text):
    """Processa a mensagem recebida e responde de acordo com o fluxo"""
    user_state = get_user_state(sender)
    current_state = user_state['state']
    message_lower = message_text.lower().strip()
    
    # Estado inicial - Pergunta sobre o app
    if current_state == ChatbotFlow.STATES['INITIAL']:
        welcome_msg = ("🎯 Olá! Seja bem-vindo(a)!\n\n"
                      "Vou te ajudar a economizar com a 99! 🚗💰\n\n"
                      "Primeiro, me conta: *Você já tem o app da 99 instalado no seu celular?*\n\n"
                      "Responda com:\n"
                      "✅ *SIM* - se já tem o app\n"
                      "❌ *NÃO* - se ainda não tem")
        
        uazapi.send_text(sender, welcome_msg)
        update_user_state(sender, ChatbotFlow.STATES['WAITING_APP_RESPONSE'])
    
    # Aguardando resposta sobre ter o app
    elif current_state == ChatbotFlow.STATES['WAITING_APP_RESPONSE']:
        if any(word in message_lower for word in ['sim', 'tenho', 'já tenho', 's', 'yes', 'claro']):
            # Usuário tem o app - pergunta sobre cupom
            cupom_msg = ("Ótimo! 🎉\n\n"
                        "Agora me conta: *Você já usou algum cupom de desconto na 99?*\n\n"
                        "Responda com:\n"
                        "✅ *JÁ USEI* - se já utilizou cupom\n"
                        "❌ *NUNCA USEI* - se nunca utilizou")
            
            uazapi.send_text(sender, cupom_msg)
            update_user_state(sender, ChatbotFlow.STATES['WAITING_CUPOM_RESPONSE'])
        
        elif any(word in message_lower for word in ['não', 'nao', 'n', 'no', 'nunca', 'ainda não']):
            # Usuário não tem o app - envia links
            links_msg = ("📱 Sem problemas! Vamos resolver isso agora!\n\n"
                        "Baixe o app da 99 através dos links abaixo:\n\n"
                        f"📱 *Android (Play Store):*\n{PLAYSTORE_LINK}\n\n"
                        f"🍎 *iPhone (App Store):*\n{APPSTORE_LINK}\n\n"
                        "Depois de instalar, volte aqui que eu te ensino a economizar! 💰")
            
            uazapi.send_text(sender, links_msg)
            
            # Aguarda um tempo e pergunta novamente
            followup_msg = "Já instalou o app? Me avise quando estiver pronto! 😊"
            uazapi.send_text(sender, followup_msg)
            update_user_state(sender, ChatbotFlow.STATES['WAITING_APP_RESPONSE'])
        
        else:
            # Resposta não reconhecida
            retry_msg = ("Desculpe, não entendi sua resposta. 🤔\n\n"
                        "Por favor, responda com *SIM* ou *NÃO*:\n"
                        "Você já tem o app da 99 instalado?")
            uazapi.send_text(sender, retry_msg)
    
    # Aguardando resposta sobre cupom
    elif current_state == ChatbotFlow.STATES['WAITING_CUPOM_RESPONSE']:
        if any(word in message_lower for word in ['nunca', 'não', 'nao', 'n', 'ainda não', 'nunca usei']):
            # Nunca usou cupom - envia tutorial
            tutorial_msg = ("🎬 Perfeito! Vou te ensinar como usar cupons de desconto!\n\n"
                          "Assista este vídeo tutorial rápido e prático:")
            
            uazapi.send_text(sender, tutorial_msg)
            
            # Envia o vídeo
            video_caption = "📹 Tutorial: Como usar cupons de desconto na 99"
            uazapi.send_media(sender, VIDEO_TUTORIAL_URL, video_caption, "video")
            
            # Pergunta se deu certo
            feedback_msg = ("Depois de assistir o vídeo e aplicar o cupom...\n\n"
                           "*Conseguiu utilizar o cupom com sucesso?* 🎯\n\n"
                           "Responda com:\n"
                           "✅ *SIM* - consegui usar!\n"
                           "❌ *NÃO* - tive problemas")
            
            uazapi.send_text(sender, feedback_msg)
            update_user_state(sender, ChatbotFlow.STATES['WAITING_TUTORIAL_FEEDBACK'])
        
        elif any(word in message_lower for word in ['sim', 'já', 'ja', 's', 'usei', 'já usei']):
            # Já usou cupom - mensagem de sucesso
            success_msg = ("👏 Parabéns! Você já está economizando!\n\n"
                          "Mas não para por aí! Temos muito mais ofertas esperando por você! 🎁\n\n"
                          f"*Entre no nosso grupo VIP de ofertas:*\n{GRUPO_OFERTAS_LINK}\n\n"
                          "No grupo você recebe:\n"
                          "✅ Cupons exclusivos diariamente\n"
                          "✅ Promoções antecipadas\n"
                          "✅ Dicas para economizar ainda mais\n\n"
                          "Te vejo lá! 🚀")
            
            uazapi.send_text(sender, success_msg)
            update_user_state(sender, ChatbotFlow.STATES['COMPLETED'])
        
        else:
            # Resposta não reconhecida
            retry_msg = ("Desculpe, não entendi. 🤔\n\n"
                        "Você já usou algum cupom de desconto na 99?\n"
                        "Responda com *JÁ USEI* ou *NUNCA USEI*")
            uazapi.send_text(sender, retry_msg)
    
    # Aguardando feedback do tutorial
    elif current_state == ChatbotFlow.STATES['WAITING_TUTORIAL_FEEDBACK']:
        if any(word in message_lower for word in ['sim', 'consegui', 'deu certo', 's', 'funcionou']):
            # Tutorial funcionou - envia link do grupo
            congrats_msg = ("🎉 Excelente! Fico feliz que tenha conseguido!\n\n"
                          "Agora você já sabe economizar! Mas isso é só o começo...\n\n"
                          f"*Entre no nosso grupo VIP de ofertas:*\n{GRUPO_OFERTAS_LINK}\n\n"
                          "Benefícios do grupo:\n"
                          "🎁 Cupons exclusivos todos os dias\n"
                          "💰 Economize até 50% nas corridas\n"
                          "🔥 Promoções em primeira mão\n"
                          "👥 Comunidade de economia compartilhada\n\n"
                          "Nos vemos lá! 🚀")
            
            uazapi.send_text(sender, congrats_msg)
            update_user_state(sender, ChatbotFlow.STATES['COMPLETED'])
        
        elif any(word in message_lower for word in ['não', 'nao', 'n', 'problema', 'erro', 'não consegui']):
            # Teve problemas - oferece ajuda
            help_msg = ("😔 Poxa, vamos resolver isso!\n\n"
                       "Tente seguir estes passos:\n\n"
                       "1️⃣ Abra o app da 99\n"
                       "2️⃣ Toque no menu (≡)\n"
                       "3️⃣ Selecione 'Cupons'\n"
                       "4️⃣ Digite o código do cupom\n"
                       "5️⃣ Toque em 'Aplicar'\n\n"
                       "Se ainda tiver problemas, entre em contato com o suporte da 99.\n\n"
                       "Conseguiu agora? Responda *SIM* ou *NÃO*")
            
            uazapi.send_text(sender, help_msg)
        
        else:
            # Resposta não reconhecida
            retry_msg = ("Por favor, me diga:\n"
                        "Conseguiu usar o cupom depois de assistir o tutorial?\n"
                        "Responda com *SIM* ou *NÃO*")
            uazapi.send_text(sender, retry_msg)
    
    # Estado completo - reinicia conversa se necessário
    elif current_state == ChatbotFlow.STATES['COMPLETED']:
        restart_msg = ("Olá novamente! 😊\n\n"
                      "Já estou te ajudando com os cupons da 99.\n"
                      f"Não esqueça de entrar no grupo: {GRUPO_OFERTAS_LINK}\n\n"
                      "Precisa de mais alguma coisa?")
        uazapi.send_text(sender, restart_msg)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint do webhook que recebe as mensagens do Uazapi"""
    try:
        data = request.json
        logger.info(f"Webhook recebido: {json.dumps(data, indent=2)}")
        
        # Verifica se é uma mensagem recebida
        if data.get('event') == 'messages.upsert':
            messages = data.get('data', {}).get('messages', [])
            
            for msg in messages:
                # Processa apenas mensagens de texto recebidas
                if msg.get('type') == 'text' and not msg.get('fromMe'):
                    sender = msg.get('from')
                    message_text = msg.get('body', '')
                    
                    logger.info(f"Mensagem de {sender}: {message_text}")
                    
                    # Processa a mensagem
                    process_message(sender, message_text)
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check para o Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'instance_id': UAZAPI_INSTANCE_ID
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Página inicial"""
    return jsonify({
        'message': 'Bot WhatsApp 99 - Uazapi',
        'status': 'running',
        'endpoints': {
            'webhook': '/webhook',
            'health': '/health'
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)