import os 
import psycopg2
import redis
import json
from bottle import Bottle, request, response, hook
from datetime import datetime

class Sender(Bottle):
    def __init__(self):
        super().__init__()
        print(os.getenv('DB_NAME'))
        print(os.getenv('DB_USER'))
        print(os.getenv('DB_PASS'))
        print(os.getenv('DB_HOST'))
        print(os.getenv('REDIS_HOST'))

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

    def index(self):
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
            print(f"[DB] Attempting to connect with DSN: {self.dsn}")
            with psycopg2.connect(self.dsn, connect_timeout=5) as conn:
                print("[DB] Connection successful!")
                with conn.cursor() as cur:
                    cur.execute(SQL, (now, assunto, mensagem, email))
                    conn.commit()
                    print("[DB] Insert successful!")
        except Exception as e:
            print(f"[DB ERROR] {e}")
            raise

        # Check if Redis is disabled via environment variable
        redis_disabled = os.getenv('REDIS_DISABLED', 'false').lower() == 'true'
        
        if redis_disabled:
            print("[REDIS] Redis disabled via REDIS_DISABLED=true")
            msg = {'data': now.isoformat(), 'assunto': assunto, 'mensagem': mensagem, 'email': email}
            print(f"[REDIS] Message would be sent: {json.dumps(msg)}")
            return
        
        try:
            print(f"[REDIS] Attempting to connect to Redis at {self.fila.connection_pool.connection_kwargs}")
            
            # Test connection first
            self.fila.ping()
            print("[REDIS] Connection test successful!")
            
            msg = {'data': now.isoformat(), 'assunto': assunto, 'mensagem': mensagem, 'email': email}
            msg_json = json.dumps(msg)
            print(f"[REDIS] Message JSON: {msg_json}")
            
            result = self.fila.rpush('sender', msg_json)
            print(f'[REDIS] Message pushed to queue successfully! Queue length: {result}')
        except Exception as e:
            print(f"[REDIS ERROR] {e}")
            print(f"[REDIS ERROR] Error type: {type(e)}")
            print("[REDIS] Continuing without Redis...")
            # Don't raise the exception, just log it
            # raise

        print('[OK] Mensagem registrada e enfileirada!')

    def send(self):
        try:
            print(f"[REQUEST] Received POST to /api")
            print(f"[REQUEST] Content-Type: {request.content_type}")
            print(f"[REQUEST] Forms: {dict(request.forms)}")
            
            assunto = request.forms.get('assunto')
            mensagem = request.forms.get('mensagem')
            email = request.forms.get('email')

            print(f"[REQUEST] Extracted - assunto: {assunto}, mensagem: {mensagem}, email: {email}")

            if not (assunto and mensagem and email):
                response.status = 400
                error_msg = "Campos obrigatórios: assunto, mensagem, email."
                print(f"[ERROR] {error_msg}")
                return error_msg

            print(f"[RECEBIDO] assunto={assunto} email={email}")
            self.register_message(assunto, mensagem, email)

            success_msg = f'Mensagem enfileirada! Assunto: {assunto} Mensagem: {mensagem} Email: {email}'
            print(f"[SUCCESS] {success_msg}")
            return success_msg
        except Exception as e:
            response.status = 500
            error_msg = f"[ERRO] {e}"
            print(error_msg)
            return str(e)

if __name__ == '__main__':
    sender = Sender()
    sender.run(host='0.0.0.0', port=8080, debug=True)
