from fastapi import APIRouter

from app.api.endpoints.health.health_check import router as health_check_router
from app.api.endpoints.user.create_user import router as create_user_router
from app.api.endpoints.user.login import router as login_router
from app.api.endpoints.user.get_user import router as get_user_router
from app.api.endpoints.chatbot.create_message import router as create_message_router
from app.api.endpoints.chatbot.get_chat_history import router as get_chat_history_router
# from app.api.v1.endpoints.user import router as user_router

routers = APIRouter()
router_list = [health_check_router, create_user_router, login_router, get_user_router,
               create_message_router, get_chat_history_router]

for router in router_list:
    router.tags = routers.tags.append("v1")
    routers.include_router(router)