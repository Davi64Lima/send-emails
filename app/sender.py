import os 
import psycopg2
import redis
import json
from bottle import Bottle, request, response

class Sender(Bottle):
    def __init__(self):
        super().__init__()
        self.dsn = f"dbname={os.getenv('DB_NAME', 'email_sender')} " \
                   f"user={os.getenv('DB_USER', 'postgres')} " \
                   f"password={os.getenv('DB_PASS', 'postgres')} " \
                   f"host={os.getenv('DB_HOST', 'db')}"

        redis_host = os.getenv('REDIS_HOST', 'queue') 
        self.fila = redis.StrictRedis(host=redis_host, port=6379, db=0)
        self.route('/api', method='POST', callback=self.send)
        self.route('/', method='GET', callback=self.index)

    def index(self):
        return "To rodando papai!!"

    def register_message(self, assunto, mensagem, email):
        SQL = 'INSERT INTO emails (assunto, mensagem, email) VALUES (%s, %s, %s)'

        try:
            # Abre conexão e cursor com contexto (seguro)
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(SQL, (assunto, mensagem, email))
                    conn.commit()
        except Exception as e:
            print(f"[DB ERROR] {e}")
            raise

        msg = {'assunto': assunto, 'mensagem': mensagem, 'email': email}
        self.fila.rpush('sender', json.dumps(msg))
        print('[OK] Mensagem registrada e enfileirada!')

    def send(self):
        try:
            assunto = request.forms.get('assunto')
            mensagem = request.forms.get('mensagem')
            email = request.forms.get('email')

            if not (assunto and mensagem and email):
                response.status = 400
                return "Campos obrigatórios: assunto, mensagem, email."

            print(f"[RECEBIDO] assunto={assunto} email={email}")
            self.register_message(assunto, mensagem, email)

            return f'Mensagem enfileirada! Assunto: {assunto} Mensagem: {mensagem} Email: {email}'
        except Exception as e:
            response.status = 500
            print(f"[ERRO] {e}")
            return "Erro interno ao processar a mensagem."

if __name__ == '__main__':
    sender = Sender()
    sender.run(host='0.0.0.0', port=8080, debug=True)
