from openai import OpenAI
from typing import List, Dict

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_completion(self, prompt: str, model: str = "text-davinci-003", max_tokens: int = 100, temperature: float = 0.7) -> str:
        try:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"❌ Error generating completion: {e}")
            return None

    def generate_chat_response(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            content = response.choices[0].message.content.strip()

            # ✅ Token count
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            print(f"📊 Tokens usados: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")

            return {
                "content": content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        except Exception as e:
            print(f"❌ Error generating chat response: {e}")
            return None

