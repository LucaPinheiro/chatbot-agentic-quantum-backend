# env.py  (na raiz)

import os
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

settings = SimpleNamespace(
    # --- API ---
    API_V1_STR="/api",
    PROJECT_NAME=os.getenv("PROJECT_NAME", "Quantum Tutor Chatbot"),
    DESCRIPTION=os.getenv(
        "DESCRIPTION",
        "Chatbot tutor de computação quântica com RAG e multi‑agentes",
    ),
    VERSION=os.getenv("VERSION", "0.1.0"),

    # --- Flags ---
    DEBUG=os.getenv("DEBUG", "true").lower() == "true",

    # --- CORS (lista separada por vírgula) ---
    BACKEND_CORS_ORIGINS=[
        o.strip() for o in os.getenv("BACKEND_CORS_ORIGINS", "*").split(",")
    ],

    # --- Bancos / filas (use se precisar) ---
    POSTGRES_HOST=os.getenv("POSTGRES_HOST"),
    POSTGRES_PORT=int(os.getenv("POSTGRES_PORT", 5432)),
    POSTGRES_USER=os.getenv("POSTGRES_USER"),
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD"),
    POSTGRES_DB=os.getenv("POSTGRES_DB"),
    REDIS_HOST=os.getenv("REDIS_HOST"),
    REDIS_PORT=int(os.getenv("REDIS_PORT", 6379)),
)
