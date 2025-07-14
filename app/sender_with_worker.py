import os 
import psycopg2
import redis
import json
import logging
import sys
import threading
import time
from bottle import Bottle, request, response, hook
from datetime import datetime

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class WorkerThread(threading.Thread):
    """Worker que roda em background para processar emails"""
    
    def __init__(self, redis_host, resend_api_key, from_email):
        super().__init__()
        self.redis_host = redis_host
        self.resend_api_key = resend_api_key
        self.from_email = from_email
        self.daemon = True  # Thread morre quando a aplicação principal morre
        self.running = True
        
    def run(self):
        logger.info("=== Starting Worker Thread ===")
        
        try:
            import resend
            resend.api_key = self.resend_api_key
            
            redis_conn = redis.Redis(
                host=self.redis_host, 
                port=6379, 
                db=0,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Testa a conexão
            redis_conn.ping()
            logger.info("✅ Worker: Conexão com Redis estabelecida")
            
        except Exception as e:
            logger.error(f"❌ Worker: Erro ao conectar com Redis: {e}")
            return
        
        logger.info('🚀 Worker iniciado!')
        logger.info(f'📧 Email remetente: {self.from_email}')
        logger.info('⏳ Aguardando mensagens na fila "sender"...')

        message_count = 0
        error_count = 0

        while self.running:
            try:
                logger.info("🔍 Worker: Verificando mensagens na fila...")
                
                # Espera uma nova mensagem na fila 'sender'
                result = redis_conn.blpop('sender', timeout=5)
                if result is None:
                    logger.info("⏰ Worker: Timeout - Nenhuma mensagem na fila")
                    continue
                    
                mensagem_raw = result[1]
                message_count += 1
                
                logger.info(f"📨 Worker: Mensagem #{message_count} capturada do Redis")
                
                # Decodifica e valida a mensagem
                try:
                    mensagem = json.loads(mensagem_raw)
                    logger.info(f"✅ Worker: Mensagem JSON decodificada com sucesso")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Worker: Erro ao decodificar JSON: {e}")
                    error_count += 1
                    continue
                
                # Valida os campos da mensagem
                required_fields = ['email', 'assunto', 'mensagem']
                missing_fields = [field for field in required_fields if field not in mensagem]
                
                if missing_fields:
                    logger.error(f"❌ Worker: Campos obrigatórios ausentes: {missing_fields}")
                    error_count += 1
                    continue
                
                if not mensagem['email'] or not mensagem['assunto'] or not mensagem['mensagem']:
                    logger.error("❌ Worker: Campos obrigatórios não podem estar vazios")
                    error_count += 1
                    continue
                
                logger.info(f"✅ Worker: Mensagem validada")
                logger.info(f"📧 Worker: Enviando email para: {mensagem['email']}")
                logger.info(f"📝 Worker: Assunto: {mensagem['assunto']}")

                # Envia o e-mail
                email_response = resend.Emails.send({
                    "from": self.from_email,
                    "to": mensagem['email'],
                    "subject": mensagem['assunto'],
                    "html": mensagem['mensagem']
                })

                logger.info(f"✅ Worker: Email enviado com sucesso!")
                logger.info(f"📊 Worker: Resposta do Resend: {email_response}")
                logger.info(f"📈 Worker: Estatísticas - Mensagens processadas: {message_count}, Erros: {error_count}")

            except redis.exceptions.TimeoutError:
                logger.info("⏰ Worker: Timeout - Nenhuma mensagem na fila nos últimos 5 segundos")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Worker: Erro ao processar mensagem: {e}")
                logger.info(f"📈 Worker: Estatísticas - Mensagens processadas: {message_count}, Erros: {error_count}")
                time.sleep(2)  # Espera antes de tentar novamente
    
    def stop(self):
        """Para o worker"""
        self.running = False
        logger.info("🛑 Worker: Parando worker thread")

class Sender(Bottle):
    def __init__(self):
        super().__init__()
        logger.info("=== Starting Sender Application ===")
        logger.info(f"DB_NAME: {os.getenv('DB_NAME')}")
        logger.info(f"DB_USER: {os.getenv('DB_USER')}")
        logger.info(f"DB_PASS: {os.getenv('DB_PASS')}")
        logger.info(f"DB_HOST: {os.getenv('DB_HOST')}")
        logger.info(f"REDIS_HOST: {os.getenv('REDIS_HOST')}")

        self.dsn = f"dbname={os.getenv('DB_NAME', 'email_sender')} " \
                   f"user={os.getenv('DB_USER', 'postgres')} " \
                   f"password={os.getenv('DB_PASS', 'postgres')} " \
                   f"host={os.getenv('DB_HOST', 'db')}"

        redis_host = os.getenv('REDIS_HOST', 'queue') 
        self.fila = redis.StrictRedis(
            host=redis_host, 
            port=6379, 
            db=0,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )

        # Rotas
        self.route('/api', method='POST', callback=self.send)
        self.route('/', method='GET', callback=self.index)
        self.add_hook('after_request', self.enable_cors)
        
        # Iniciar worker em background
        self.start_worker()
        
        logger.info("=== Sender Application initialized successfully ===")

    def start_worker(self):
        """Inicia o worker em background"""
        try:
            redis_host = os.getenv('REDIS_HOST', 'queue')
            resend_api_key = os.getenv('RESEND_API_KEY')
            from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
            
            if not resend_api_key:
                logger.warning("⚠️ RESEND_API_KEY não configurada - Worker não iniciado")
                return
            
            self.worker_thread = WorkerThread(redis_host, resend_api_key, from_email)
            self.worker_thread.start()
            logger.info("✅ Worker thread iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar worker: {e}")

    def index(self):
        logger.info("Health check endpoint accessed")
        return "To rodando papai!!"

    def enable_cors(self):
        # Permitir origem do frontend
        response.headers['Access-Control-Allow-Origin'] = os.getenv(
            'ALLOWED_ORIGIN', 'https://sender-email-client-production.up.railway.app')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'

    def register_message(self, assunto, mensagem, email):
        SQL = 'INSERT INTO emails (data, assunto, mensagem, email) VALUES (%s, %s, %s, %s)'
        now = datetime.utcnow()

        try:
            logger.info(f"[DB] Attempting to connect with DSN: {self.dsn}")
            with psycopg2.connect(self.dsn, connect_timeout=5) as conn:
                logger.info("[DB] Connection successful!")
                with conn.cursor() as cur:
                    cur.execute(SQL, (now, assunto, mensagem, email))
                    conn.commit()
                    logger.info("[DB] Insert successful!")
        except Exception as e:
            logger.error(f"[DB ERROR] {e}")
            raise

        # Check if Redis is disabled via environment variable
        redis_disabled = os.getenv('REDIS_DISABLED', 'false').lower() == 'true'
        
        if redis_disabled:
            logger.info("[REDIS] Redis disabled via REDIS_DISABLED=true")
            msg = {'data': now.isoformat(), 'assunto': assunto, 'mensagem': mensagem, 'email': email}
            logger.info(f"[REDIS] Message would be sent: {json.dumps(msg)}")
            return
        
        try:
            logger.info(f"[REDIS] Attempting to connect to Redis at {self.fila.connection_pool.connection_kwargs}")
            
            # Test connection first
            self.fila.ping()
            logger.info("[REDIS] Connection test successful!")
            
            msg = {'data': now.isoformat(), 'assunto': assunto, 'mensagem': mensagem, 'email': email}
            msg_json = json.dumps(msg)
            logger.info(f"[REDIS] Message JSON: {msg_json}")
            
            result = self.fila.rpush('sender', msg_json)
            logger.info(f'[REDIS] Message pushed to queue successfully! Queue length: {result}')
        except Exception as e:
            logger.error(f"[REDIS ERROR] {e}")
            logger.error(f"[REDIS ERROR] Error type: {type(e)}")
            logger.warning("[REDIS] Continuing without Redis...")
            # Don't raise the exception, just log it
            # raise

        logger.info('[OK] Mensagem registrada e enfileirada!')

    def send(self):
        try:
            logger.info(f"[REQUEST] Received POST to /api")
            logger.info(f"[REQUEST] Content-Type: {request.content_type}")
            logger.info(f"[REQUEST] Forms: {dict(request.forms)}")
            
            assunto = request.forms.get('assunto')
            mensagem = request.forms.get('mensagem')
            email = request.forms.get('email')

            logger.info(f"[REQUEST] Extracted - assunto: {assunto}, mensagem: {mensagem}, email: {email}")

            if not (assunto and mensagem and email):
                response.status = 400
                error_msg = "Campos obrigatórios: assunto, mensagem, email."
                logger.error(f"[ERROR] {error_msg}")
                return error_msg

            logger.info(f"[RECEBIDO] assunto={assunto} email={email}")
            self.register_message(assunto, mensagem, email)

            success_msg = f'Mensagem enfileirada! Assunto: {assunto} Mensagem: {mensagem} Email: {email}'
            logger.info(f"[SUCCESS] {success_msg}")
            return success_msg
        except Exception as e:
            response.status = 500
            error_msg = f"[ERRO] {e}"
            logger.error(error_msg)
            return str(e)

if __name__ == '__main__':
    logger.info("=== Starting Sender Application with Worker ===")
    sender = Sender()
    logger.info("Starting Bottle server on 0.0.0.0:8080")
    sender.run(host='0.0.0.0', port=8080, debug=True) 