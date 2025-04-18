from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.schemas.health_check import HealthCheckResponse



# --------- Use‑case --------- #
class HealthCheckUseCase:
    def execute(self) -> HealthCheckResponse:
        return HealthCheckResponse(
            status="ok",
            message="Serviço funcionando normalmente",
        )


# -------- Controller -------- #
class HealthCheckController:
    def __init__(self, usecase: HealthCheckUseCase) -> None:
        self.usecase = usecase

    def handle(self) -> HealthCheckResponse:
        return self.usecase.execute()


# --------- DI helpers ------- #
def get_usecase() -> HealthCheckUseCase:
    return HealthCheckUseCase()


def get_controller(
    usecase: HealthCheckUseCase = Depends(get_usecase),
) -> HealthCheckController:
    return HealthCheckController(usecase)


# ----------- Router --------- #
router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check(
    controller: HealthCheckController = Depends(get_controller),
) -> HealthCheckResponse:
    return controller.handle()
