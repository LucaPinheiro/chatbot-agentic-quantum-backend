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
            cutoff = record.get("summary_cutoff")
            pk = f"session#{session_id}"

            items = self._fetch_all_items(pk)
            print("🔍 Itens recebidos:", items)
            messages = self._filter_messages(items, cutoff)
            if not messages:
                continue

            prompt = "\n".join([f"{m['role']}: {m['message']}" for m in messages])
            summary = self._generate_summary(prompt)
            self._save_summary(pk, summary)

        return {"statusCode": 200}

    def _fetch_all_items(self, pk):
        response = self.dynamo.query(KeyConditionExpression=Key("PK").eq(pk))
        return response["Items"]

    def _filter_messages(self, items, cutoff):
        items = sorted(items, key=lambda x: x["SK"])
        messages = [i for i in items if i["type"] == "message"]
        if cutoff:
            messages = [m for m in messages if m["timestamp"] > cutoff]
        return messages

    def _generate_summary(self, conversation):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "Resuma didaticamente esse trecho da conversa para monitoramento pedagógico."},
                {"role": "user", "content": conversation}
            ]
        )
        return response.choices[0].message.content

    def _save_summary(self, pk, summary_text):
        self.dynamo.put_item(Item={
            "PK": pk,
            "SK": "summary",
            "type": "summary",
            "summary": summary_text,
            "timestamp": datetime.now(tz=timezone.utc).isoformat()
        })


def handler(event, context):
    service = SummarizationService()
    return service.process(SQSEvent(event))
