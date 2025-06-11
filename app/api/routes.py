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
from app.api.endpoints.group.delete_group import router as delete_group_router
from app.api.endpoints.classes.delete_class import router as delete_class_router
from app.api.endpoints.group.create_group import router as create_group_router
from app.api.endpoints.classes.get_all_classes import router as get_all_classes_router
# from app.api.endpoints.classes.update_class import router as update_class_router
from app.api.endpoints.group.update_group import router as update_group_router
from app.api.endpoints.group.get_group_by_id import router as get_group_by_id_router
from app.api.endpoints.user.delete_user import router as delete_user_router
from app.api.endpoints.classes.create_class import router as create_class_router
from app.api.endpoints.group_enrollment.add_user_group import router as add_user_group_router
from app.api.endpoints.class_topics.delete_topics_by_id import router as delete_topics_by_id_router
from app.api.endpoints.user.update_user import router as update_user_router
from app.api.endpoints.group.get_all_groups import router as get_all_groups_router
from app.api.endpoints.class_topics.add_topics_to_class import router as add_topics_to_class_router
from app.api.endpoints.class_topics.get_all_progress_class import router as get_all_progress_class_router
from app.api.endpoints.class_topics.get_progress_percentual_by_group import router as get_progress_percentual_by_group_router
from app.api.endpoints.classes.get_all_classes_by_user import router as get_all_classes_by_user_router
from app.api.endpoints.chatbot.get_session import router as get_session_router
from app.api.endpoints.group_enrollment.delete_user_from_group import router as delete_user_from_group_router

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
    delete_group_router,
    delete_class_router,
    create_group_router,
    get_all_classes_router,
    # update_class_router,
    update_group_router,
    get_group_by_id_router,
    delete_user_router,
    create_class_router,
    # add_user_group_router,
    delete_topics_by_id_router,
    create_class_router,
    update_user_router,
    get_all_groups_router,
    add_topics_to_class_router,
    get_all_progress_class_router,
    get_progress_percentual_by_group_router,
    get_all_classes_by_user_router,
    create_class_router,
    get_session_router, 
    delete_user_from_group_router
]

for router in router_list:
    router.tags = ["v1"]
    routers.include_router(router)