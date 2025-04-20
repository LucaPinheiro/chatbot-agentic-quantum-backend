# src/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import routers
import uvicorn

from app.core.settings import load_settings

# Carrega configurações
settings = load_settings()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        description=settings.description,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_str}/openapi.json",
    )

    if settings.debug:
        print("CORS habilitado para desenvolvimento.")
        print(f"Servidor rodando em http://0.0.0.0:8000 🚀 {settings.app_env.value}")
        

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routers, prefix=settings.api_v1_str)
    return app

app = create_app()

if __name__ == "__main__":


    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
