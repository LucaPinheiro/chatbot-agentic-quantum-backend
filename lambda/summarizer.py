import os
import boto3
from datetime import datetime, timezone
from openai import OpenAI
from schemas.sqs import SQSEvent
from boto3.dynamodb.conditions import Key


class SummarizationService:
    def __init__(self):
        self.dynamo = boto3.resource("dynamodb").Table(os.environ["DYNAMO_TABLE"])
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def process(self, sqs_event):
        for record in sqs_event:
            session_id = record["session_id"]
            cutoff = record.get("summary_cutoff") or "0000-01-01T00:00:00Z"
            pk = f"session#{session_id}"

            items = self._fetch_all_items(pk)
            print(f"🔍 Itens recebidos para {session_id}: {len(items)}")

            messages = self._filter_messages_since_cutoff(items, cutoff)
            print(f"📤 Mensagens novas após cutoff {cutoff}: {len(messages)}")

            if not messages:
                print("⚠️ Nenhuma nova mensagem para resumir.")
                continue

            previous_summary = self._fetch_previous_summary(pk)
            conversation = "\n".join([f"{m['role']}: {m['message']}" for m in messages])

            if previous_summary:
                prompt = f"""
                    Resumo anterior da conversa:

                    {previous_summary}

                    Agora considere também os trechos abaixo (últimas mensagens trocadas entre o usuário e o sistema), e produza um novo resumo didático consolidado, mantendo o contexto anterior e incluindo os novos elementos:

                    {conversation}""".strip()
            else:
                prompt = f"""
                    A seguir estão as últimas mensagens trocadas entre o usuário e o sistema.

                    Crie um resumo didático com base nesse trecho da conversa para fins de acompanhamento pedagógico:

                    {conversation}""".strip()

            summary, total_tokens = self._generate_summary(prompt)
            self._save_summary(pk, summary, total_tokens)
            print(f"✅ Novo resumo salvo com sucesso. Tokens usados: {total_tokens}")

        return {"statusCode": 200}

    def _fetch_all_items(self, pk):
        response = self.dynamo.query(KeyConditionExpression=Key("PK").eq(pk))
        return response["Items"]

    def _fetch_previous_summary(self, pk):
        response = self.dynamo.get_item(Key={"PK": pk, "SK": "summary"})
        return response.get("Item", {}).get("summary")

    def _filter_messages_since_cutoff(self, items, cutoff: str):
        items = sorted(items, key=lambda x: x["SK"])
        messages = [
            m for m in items
            if m.get("type") == "message"
            and "timestamp" in m
            and m["timestamp"] > cutoff
        ]
        return messages

    def _generate_summary(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente pedagógico. Gere um resumo claro e didático da conversa."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        content = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        return content, total_tokens

    def _save_summary(self, pk, summary_text, total_tokens):
        now = datetime.now(timezone.utc).isoformat()
        self.dynamo.put_item(Item={
            "PK": pk,
            "SK": "summary",
            "type": "summary",
            "summary": summary_text,
            "tokens": total_tokens,
            "timestamp": now
        })


def handler(event, context):
    service = SummarizationService()
    return service.process(SQSEvent(event))
