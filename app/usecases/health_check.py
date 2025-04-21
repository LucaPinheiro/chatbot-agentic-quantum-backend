from app.schemas.health_check import HealthCheckResponse

class HealthCheckUseCase:
    def execute(self) -> HealthCheckResponse:
        """
        Executa o caso de uso de verificação de saúde da aplicação.
        
        Returns:
            HealthCheckResponse: Resposta com o status da aplicação
        """
        return HealthCheckResponse(
            status="ok",
            message="API está funcionando corretamente"
        ) 