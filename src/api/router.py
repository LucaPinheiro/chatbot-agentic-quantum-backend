from fastapi import APIRouter

# ➊ Importe o módulo da rota (ele já contém um APIRouter interno)
from src.api.routes import health_check

api_router = APIRouter()
api_router.include_router(health_check.router)   # ➋ Agrega a rota

__all__ = ["api_router"]
