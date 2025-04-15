# src/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Carregar variáveis do .env
from src.env import *

# Importar routers (API modular por aula)
from src.app.api.router import api_router  # você pode dividir por aulas depois

# Inicialização da aplicação
app = FastAPI(
    title="Quantum Tutor Chatbot",
    description="Chatbot tutor de computação quântica com RAG e multi-agentes",
    version="0.1.0"
)

# CORS Middleware (ajustar conforme necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ em produção, troque por domínios seguros
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas principais da API
app.include_router(api_router, prefix="/api")

# Health check básico
@app.get("/")
async def root():
    return {"message": "Quantum Tutor Chatbot is running 🚀"}
