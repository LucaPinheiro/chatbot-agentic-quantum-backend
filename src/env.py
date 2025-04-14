# env.py
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env, se existir na raiz do projeto
load_dotenv()

# Exemplo de uso: acesso às variáveis
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

if __name__ == "__main__":
    # Apenas para testar se as variáveis estão sendo carregadas corretamente
    print("Configuração do PostgreSQL:")
    print(f"Host: {POSTGRES_HOST}")
    print(f"Port: {POSTGRES_PORT}")
    print(f"User: {POSTGRES_USER}")
    print(f"DB: {POSTGRES_DB}")
    print("\nConfiguração do Redis:")
    print(f"Host: {REDIS_HOST}")
    print(f"Port: {REDIS_PORT}")
