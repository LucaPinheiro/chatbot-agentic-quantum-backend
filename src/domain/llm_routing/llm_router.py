from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
from langchain.chat_models import ChatOpenAI

class ModelType(str, Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-2"
    PALM = "palm-2" 
    LLAMA = "llama-2"

class LLMConfig(BaseModel):
    model_type: ModelType
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0

class LLMRouter:
    """Roteador para múltiplos modelos de LLM"""
    
    def __init__(self):
        self.models: Dict[ModelType, ChatOpenAI] = {}
        self._setup_models()
        
    def _setup_models(self):
        """Configura os modelos disponíveis"""
        configs = {
            ModelType.GPT4: LLMConfig(
                model_type=ModelType.GPT4,
                temperature=0.7,
                max_tokens=2000,
            ),
            ModelType.GPT35: LLMConfig(
                model_type=ModelType.GPT35,
                temperature=0.8,
                max_tokens=4000
            ),
            ModelType.CLAUDE: LLMConfig(
                model_type=ModelType.CLAUDE,
                temperature=0.6,
                max_tokens=8000
            ),
            ModelType.LLAMA: LLMConfig(
                model_type=ModelType.LLAMA,
                temperature=0.9,
                max_tokens=2000
            )
        }
        
        for model_type, config in configs.items():
            self.models[model_type] = ChatOpenAI(
                model_name=config.model_type,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p
            )
    
    def get_model(self, model_type: ModelType) -> ChatOpenAI:
        """Retorna um modelo específico"""
        if model_type not in self.models:
            raise ValueError(f"Modelo {model_type} não encontrado")
        return self.models[model_type]
    
    def get_available_models(self) -> List[ModelType]:
        """Retorna lista de modelos disponíveis"""
        return list(self.models.keys())
    
    async def route_prompt(self, prompt: str, model_type: ModelType) -> str:
        """Roteia um prompt para o modelo especificado"""
        model = self.get_model(model_type)
        response = await model.agenerate([prompt])
        return response.generations[0][0].text

    async def route_prompt_to_all(self, prompt: str) -> Dict[ModelType, str]:
        """Envia o mesmo prompt para todos os modelos"""
        results = {}
        for model_type in self.models:
            results[model_type] = await self.route_prompt(prompt, model_type)
        return results
