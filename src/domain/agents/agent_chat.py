# app/infrastructure/llm/openai_chat.py
from langchain_openai import OpenAI
from pydantic_ai import OpenAIAgent
from src.api.schemas import AnswerSchema
from src.domain.entities.message import Message
from typing import List

class AgentChat:
    def __init__(self, model: str = "gpt-4-0613"):
        self.client = OpenAI()
        self.model = model

    def chat(self, history: List[Message], user_input: str) -> str:
        system_prompt = (
            "Você é um assistente especializado em AWS & DynamoDB. "
            "Responda de forma concisa, clara e didática."
        )
        
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=0.2,
            max_tokens=150
        )
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return self.model
