import redis
import json
import os 
import resend
from time import sleep
from random import randint
from datetime import datetime

# Carrega a chave da API Resend
resend.api_key = os.getenv('RESEND_API_KEY')

def validate_message(mensagem):
    """Valida se a mensagem contém todos os campos necessários"""
    required_fields = ['email', 'assunto', 'mensagem']
    missing_fields = [field for field in required_fields if field not in mensagem]
    
    if missing_fields:
        return False, f"Campos obrigatórios ausentes: {missing_fields}"
    
    if not mensagem['email'] or not mensagem['assunto'] or not mensagem['mensagem']:
        return False, "Campos obrigatórios não podem estar vazios"
    
    return True, "Mensagem válida"

def log_with_timestamp(message):
    """Adiciona timestamp aos logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def main():
    redis_host = os.getenv('REDIS_HOST', 'queue') 
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_password = os.getenv('REDIS_PASSWORD')
    
    log_with_timestamp(f"Iniciando conexão com Redis em {redis_host}:{redis_port}")
    
    try:
        # Configuração do Redis sem username fixo
        redis_conn = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            password=redis_password,
            db=0
        )
        # Testa a conexão
        redis_conn.ping()
        log_with_timestamp("✅ Conexão com Redis estabelecida com sucesso")
    except Exception as e:
        log_with_timestamp(f"❌ Erro ao conectar com Redis: {e}")
        return
    
    # Email remetente configurável
    # from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
    from_email = 'send-email@davi64lima.shop'

    log_with_timestamp('🚀 Worker iniciado!')
    log_with_timestamp(f'📧 Email remetente: {from_email}')
    log_with_timestamp('⏳ Aguardando mensagens na fila "sender"...')

    message_count = 0
    error_count = 0

    while True:
        try:
            log_with_timestamp("🔍 Verificando mensagens na fila...")
            
            # Espera uma nova mensagem na fila 'sender'
            mensagem_raw = redis_conn.blpop('sender', timeout=5)[1]
            message_count += 1
            
            log_with_timestamp(f"📨 Mensagem #{message_count} capturada do Redis")
            log_with_timestamp(f"📄 Tamanho da mensagem: {len(mensagem_raw)} bytes")
            
            # Decodifica e valida a mensagem
            try:
                mensagem = json.loads(mensagem_raw)
                log_with_timestamp(f"✅ Mensagem JSON decodificada com sucesso")
            except json.JSONDecodeError as e:
                log_with_timestamp(f"❌ Erro ao decodificar JSON: {e}")
                error_count += 1
                continue
            
            # Valida os campos da mensagem
            is_valid, validation_msg = validate_message(mensagem)
            if not is_valid:
                log_with_timestamp(f"❌ Validação falhou: {validation_msg}")
                log_with_timestamp(f"📋 Conteúdo da mensagem: {mensagem}")
                error_count += 1
                continue
            
            log_with_timestamp(f"✅ Mensagem validada: {validation_msg}")
            log_with_timestamp(f"📧 Enviando email para: {mensagem['email']}")
            log_with_timestamp(f"📝 Assunto: {mensagem['assunto']}")
            log_with_timestamp(f"📄 Tamanho do conteúdo: {len(mensagem['mensagem'])} caracteres")

            # Envia o e-mail
            email_response = resend.Emails.send({
                "from": from_email,
                "to": mensagem['email'],
                "subject": mensagem['assunto'],
                "html": mensagem['mensagem']
            })

            log_with_timestamp(f"✅ Email enviado com sucesso!")
            log_with_timestamp(f"📊 Resposta do Resend: {email_response}")
            log_with_timestamp(f"📈 Estatísticas - Mensagens processadas: {message_count}, Erros: {error_count}")

        except redis.exceptions.TimeoutError:
            log_with_timestamp("⏰ Timeout - Nenhuma mensagem na fila nos últimos 5 segundos")
            continue
        except Exception as e:
            error_count += 1
            log_with_timestamp(f"❌ Erro ao processar mensagem: {e}")
            log_with_timestamp(f"📈 Estatísticas - Mensagens processadas: {message_count}, Erros: {error_count}")
            sleep(2)  # Espera antes de tentar novamente

if __name__ == '__main__':
    main()
