# docker/Dockerfile
FROM python:3.11.8-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas os requirements (para aproveitar o cache)
COPY requirements.txt requirements-dev.txt ./

# Instala dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Em produção, descomente para copiar o código:
# COPY . .

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
