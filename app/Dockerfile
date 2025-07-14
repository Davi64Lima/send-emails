FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta correta
EXPOSE 8080

# Configurar para não bufferizar a saída (importante para logs)
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# Comando para rodar a aplicação
CMD ["python", "sender.py"] 