import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("⏳ Iniciando execução de main.py")

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.openapi.utils import get_openapi
    from app.api.routes import routers
    from app.core.settings import load_settings
except Exception as import_error:
    logger.exception("❌ Falha ao importar dependências no main.py")
    raise import_error

logger.info("✔️ Imports realizados com sucesso")


import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.routes import routers
from app.core.settings import load_settings

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega as configurações com log de erro em caso de falha
try:
    settings = load_settings()
    logger.info(f"✔️ Settings carregadas com sucesso: Stage = {settings.stage}")
except Exception as e:
    logger.exception("❌ Erro ao carregar settings:")
    raise

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Adiciona o esquema de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Aplica segurança nas rotas protegidas
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if path.startswith("/api/v1/users"):
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app() -> FastAPI:
    logger.info("🚀 Inicializando FastAPI app...")

    app = FastAPI(
        title=settings.project_name,
        description=settings.description,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_str}/openapi.json",
    )

    if settings.debug:
        logger.info("⚙️ Modo debug ativado - CORS liberado para qualquer origem.")
        logger.info(f"🌐 API rodando em http://0.0.0.0:8000 - Stage: {settings.stage.value}")
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routers, prefix=settings.api_v1_str)
    app.openapi = lambda: custom_openapi(app)

    logger.info("✅ FastAPI app criado com sucesso.")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
