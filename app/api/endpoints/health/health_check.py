from fastapi import APIRouter
from app.schemas.health_check import HealthCheckRequest, HealthCheckResponse

router = APIRouter()

class HealthCheckUseCase:
    def execute(self, request: HealthCheckRequest) -> HealthCheckResponse:
        return HealthCheckResponse(
            status="ok",
            message="Sistema funcionando corretamente"
        )

class HealthCheckController:
    def __init__(self, use_case: HealthCheckUseCase):
        self.use_case = use_case
        
    def handle(self, request: HealthCheckRequest) -> HealthCheckResponse:
        return self.use_case.execute(request)

@router.get("/health-check", response_model=HealthCheckResponse)
async def health_check(request: HealthCheckRequest = HealthCheckRequest()):
    controller = HealthCheckController(HealthCheckUseCase())
    return controller.handle(request)
