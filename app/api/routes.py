from fastapi import APIRouter

from app.api.endpoints.health.health_check import router as health_check_router
from app.api.endpoints.user.create_user import router as create_user_router
from app.api.endpoints.user.login import router as login_router
from app.api.endpoints.user.get_user_request import router as get_user_request_router
from app.api.endpoints.user.get_all_users import router as get_all_users_router
# from app.api.v1.endpoints.user import router as user_router

routers = APIRouter()
router_list = [health_check_router, create_user_router, login_router, get_user_request_router, get_all_users_router]

for router in router_list:
    router.tags = routers.tags.append("v1")
    routers.include_router(router)