from fastapi import APIRouter

from app.api.endpoints.health.health_check import router as health_check_router

from app.api.endpoints.user.create_user import router as create_user_router
from app.api.endpoints.user.login import router as login_router
from app.api.endpoints.user.get_user import router as get_user_router
from app.api.endpoints.user.get_all_users import router as get_all_users_router
from app.api.endpoints.classes.get_classes_by_group import router as get_classes_by_group_router
from app.api.endpoints.chatbot.create_message import router as create_message_router
from app.api.endpoints.chatbot.get_chat_history import router as get_chat_history_router
from app.api.endpoints.class_topics.get_class_progress_percentual_by_class import router as get_class_progress_percentual_by_class_router

routers = APIRouter()

router_list = [
    health_check_router,
    create_user_router,
    login_router,
    get_user_router,
    get_all_users_router,
    create_message_router,
    get_chat_history_router,
    get_classes_by_group_router,
    get_class_progress_percentual_by_class_router,
]

for router in router_list:
    router.tags = ["v1"]
    routers.include_router(router)