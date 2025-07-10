# 🚀 Guia de Deploy Gratuito

Este guia mostra como fazer deploy da sua aplicação de envio de e-mails em plataformas gratuitas.

## 📋 Pré-requisitos

1. **Conta no Resend**: [https://resend.com](https://resend.com) (gratuito)
2. **GitHub**: Para conectar o repositório
3. **Variáveis de ambiente**: Configure conforme cada plataforma

## 🎯 Opções de Deploy

### 1. **Railway** (Recomendado)

**Vantagens:**
- ✅ Suporte nativo a Docker
- ✅ PostgreSQL e Redis gratuitos
- ✅ Domínio gratuito
- ✅ Deploy automático

**Passos:**
1. Acesse [railway.app](https://railway.app)
2. Conecte sua conta GitHub
3. Clique em "New Project" → "Deploy from GitHub repo"
4. Selecione seu repositório
5. Adicione os serviços:
   - **PostgreSQL**: Add → Database → PostgreSQL
   - **Redis**: Add → Database → Redis
6. Configure as variáveis de ambiente:
   ```
   DB_HOST=<postgres-host>
   DB_USER=<postgres-user>
   DB_PASS=<postgres-password>
   DB_NAME=email_sender
   DB_PORT=5432
   REDIS_HOST=<redis-host>
   REDIS_PORT=6379
   RESEND_API_KEY=<sua-chave-resend>
   FROM_EMAIL=onboarding@resend.dev
   DESTINATION_EMAIL=<seu-email>
   ```
7. Deploy automático!

### 2. **Render**

**Vantagens:**
- ✅ PostgreSQL gratuito
- ✅ Redis gratuito
- ✅ Deploy automático
- ✅ Domínio gratuito

**Passos:**
1. Acesse [render.com](https://render.com)
2. Conecte sua conta GitHub
3. Clique em "New" → "Web Service"
4. Selecione seu repositório
5. Configure:
   - **Build Command**: `pip install -r app/requirements.txt`
   - **Start Command**: `python app/sender.py`
6. Adicione PostgreSQL e Redis como serviços separados
7. Configure as variáveis de ambiente
8. Deploy!

### 3. **Fly.io**

**Vantagens:**
- ✅ 3 VMs gratuitas
- ✅ PostgreSQL e Redis
- ✅ Deploy global

**Passos:**
1. Instale o Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Deploy: `fly deploy`
4. Adicione PostgreSQL: `fly postgres create`
5. Adicione Redis: `fly redis create`
6. Configure variáveis de ambiente

### 4. **Heroku** (Alternativa)

**Vantagens:**
- ✅ PostgreSQL gratuito
- ✅ Fácil deploy
- ✅ Domínio gratuito

**Limitações:**
- ❌ Sem Redis gratuito
- ❌ Sleep após 30min inativo

**Passos:**
1. Instale Heroku CLI
2. Login: `heroku login`
3. Crie app: `heroku create seu-app-name`
4. Adicione PostgreSQL: `heroku addons:create heroku-postgresql:mini`
5. Configure variáveis: `heroku config:set RESEND_API_KEY=sua-chave`
6. Deploy: `git push heroku main`

## 🔧 Configurações Específicas

### Variáveis de Ambiente Necessárias

```bash
# Banco de dados
DB_HOST=<host-do-banco>
DB_USER=<usuario>
DB_PASS=<senha>
DB_NAME=email_sender
DB_PORT=5432

# Redis
REDIS_HOST=<host-redis>
REDIS_PORT=6379

# Resend (obrigatório)
RESEND_API_KEY=<sua-chave-api>
FROM_EMAIL=onboarding@resend.dev
DESTINATION_EMAIL=<seu-email-destino>
```

### Configuração do Resend

1. Acesse [resend.com](https://resend.com)
2. Crie uma conta gratuita
3. Vá em "API Keys" → "Create API Key"
4. Copie a chave e configure nas variáveis de ambiente
5. Verifique seu domínio ou use `onboarding@resend.dev`

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco:**
   - Verifique se as variáveis de ambiente estão corretas
   - Confirme se o banco está rodando

2. **Erro de Redis:**
   - Verifique se o Redis está configurado
   - Confirme as variáveis REDIS_HOST e REDIS_PORT

3. **E-mails não enviando:**
   - Verifique se a RESEND_API_KEY está correta
   - Confirme se o FROM_EMAIL está verificado no Resend

4. **Worker não processando:**
   - Verifique se o worker está rodando
   - Confirme a conexão com Redis

## 📊 Monitoramento

### Logs
- **Railway**: Dashboard → Logs
- **Render**: Dashboard → Logs
- **Fly.io**: `fly logs`
- **Heroku**: `heroku logs --tail`

### Métricas
- **Railway**: Dashboard → Metrics
- **Render**: Dashboard → Metrics
- **Fly.io**: `fly status`

## 💡 Dicas

1. **Comece com Railway** - É o mais simples e completo
2. **Use domínios gratuitos** - Todas as plataformas oferecem
3. **Configure webhooks** - Para deploy automático
4. **Monitore logs** - Para identificar problemas
5. **Teste localmente** - Antes de fazer deploy

## 🔗 Links Úteis

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [Fly.io Documentation](https://fly.io/docs/)
- [Heroku Documentation](https://devcenter.heroku.com/)
- [Resend Documentation](https://resend.com/docs) 