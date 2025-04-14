# docker/Dockerfile
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar o Poetry (opcional, se você precisar dele para gerenciar dependências)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copiar apenas os arquivos de requisitos para aproveitar o cache do Docker
COPY requirements.txt requirements-dev.txt ./

# Instalar as dependências via pip (ou você pode optar por usar o Poetry, se preferir)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copiar o restante do código, se necessário, para containers de produção
# Para desenvolvimento, normalmente utilizamos volumes para montar os diretórios

# Variáveis de ambiente básicas
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando padrão: iniciar o servidor com Uvicorn (modo de reload para desenvolvimento)
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
