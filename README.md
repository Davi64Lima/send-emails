# Sistema de Envio de E-mails

Sistema completo para envio de e-mails usando Python, PostgreSQL, Redis e Docker.

## Arquitetura

- **App**: API Python (Bottle) para receber requisições
- **Worker**: Processamento assíncrono de e-mails
- **PostgreSQL**: Armazenamento de mensagens
- **Redis**: Fila de mensagens
- **Nginx**: Proxy reverso e servidor web
- **Frontend**: Interface HTML simples

## Pré-requisitos

- Docker e Docker Compose
- Conta no [Resend](https://resend.com) para envio de e-mails

## Configuração

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd send-emails
```

2. **Configure as variáveis de ambiente**
Crie um arquivo `.env` na raiz do projeto:
```bash
# Configurações do Banco de Dados
DB_NAME=email_sender
DB_USER=postgres
DB_PASS=postgres
DB_HOST=db
DB_PORT=5432

# Configurações do Redis
REDIS_HOST=queue

# API Key do Resend (obtenha em https://resend.com)
RESEND_API_KEY=sua_chave_aqui

# Email de destino
DESTINATION_EMAIL=seu_email@gmail.com

# Email remetente (deve ser verificado no Resend)
FROM_EMAIL=onboarding@resend.dev
```

3. **Execute o projeto**
```bash
docker-compose up -d
```

4. **Acesse a aplicação**
- Frontend: http://localhost
- API: http://localhost/api

## Como usar

1. Acesse http://localhost
2. Preencha o assunto e mensagem
3. Clique em "Enviar!"
4. O e-mail será processado pelo worker e enviado

## Estrutura do Projeto

```
send-emails/
├── app/                 # API Python
│   ├── sender.py       # Lógica principal
│   └── app.sh          # Script de inicialização
├── worker/             # Processador de e-mails
│   ├── worker.py       # Lógica do worker
│   └── dockerfile      # Imagem do worker
├── client/             # Frontend
│   └── index.html      # Interface web
├── nginx/              # Configuração do proxy
│   └── default.conf    # Configuração do Nginx
├── scripts/            # Scripts SQL
│   └── init.sql        # Inicialização do banco
├── docker-compose.yml  # Orquestração dos serviços
└── README.md          # Este arquivo
```

## Logs

Para ver os logs dos serviços:
```bash
# Todos os serviços
docker-compose logs

# Serviço específico
docker-compose logs app
docker-compose logs worker
docker-compose logs db
```

## Próximos passos

- [ ] Adicionar autenticação
- [ ] Implementar templates de e-mail
- [ ] Adicionar dashboard para monitoramento
- [ ] Implementar retry automático
- [ ] Adicionar logs estruturados
- [ ] Implementar testes automatizados
- [ ] Adicionar validação de entrada
- [ ] Implementar rate limiting 