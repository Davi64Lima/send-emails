import os 
import psycopg2
import redis
import json
import logging
import sys
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
        redis_password = os.getenv('REDIS_PASSWORD')
        self.fila = redis.StrictRedis(
            host=redis_host, 
            port=6379, 
            password=redis_password,
            db=0,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )

        # Rotas
        self.route('/api', method='POST', callback=self.send)
        self.route('/', method='GET', callback=self.index)
        self.add_hook('after_request', self.enable_cors)
        logger.info("=== Sender Application initialized successfully ===")

    def index(self):
        logger.info("Health check endpoint accessed")
        return "To rodando papai!!"

    def enable_cors(self):
        # Permitir origem do frontend
        response.headers['Access-Control-Allow-Origin'] = '*'
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
    logger.info("=== Starting Sender Application ===")
    sender = Sender()
    logger.info("Starting Bottle server on 0.0.0.0:8080")
    sender.run(host='0.0.0.0', port=8080, debug=True)
