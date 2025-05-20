from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.routes import routers
import uvicorn

from app.core.settings import load_settings

settings = load_settings()


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
        print(f"Servidor rodando em http://0.0.0.0:8000 🚀 {settings.stage.value}")
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routers, prefix=settings.api_v1_str)
    app.openapi = lambda: custom_openapi(app)  

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
