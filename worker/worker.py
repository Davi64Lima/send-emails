import redis
import json
import os 
import resend
from time import sleep
from random import randint

# Carrega a chave da API Resend
resend.api_key = os.getenv('RESEND_API_KEY')

def main():
    redis_host = os.getenv('REDIS_HOST', 'queue') 
    redis_conn = redis.Redis(host=redis_host, port=6379, db=0)

    print('Aguardando mensagens ...')

    while True:
        try:
            # Espera uma nova mensagem na fila 'sender'
            mensagem_raw = redis_conn.blpop('sender')[1]
            mensagem = json.loads(mensagem_raw)

            print(f"Mensagem recebida: {mensagem}")
            print('Mandando a mensagem:', mensagem['assunto'])

            # Envia o e-mail
            email_response = resend.Emails.send({
                "from": "onboarding@resend.dev",  # ou seu domínio verificado
                "to": 'novodavilima@gmail.com',
                "subject": mensagem['assunto'],
                "html": mensagem['mensagem']
            })

            print("Resposta do Resend:", email_response)

        except Exception as e:
            print("Erro ao processar mensagem:", e)
            sleep(2)  # Espera antes de tentar novamente

if __name__ == '__main__':
    main()
