# app/infra/repositories/chat_message_repository.py

import time
from typing import List, Optional
from uuid import uuid4

from app.infra.external.aws import DynamoConfig, DynamoDBResources


class ChatMessageRepository:
    def __init__(self, table_name: str):
        self.dynamo = DynamoDBResources(
            DynamoConfig(
                table_name=table_name,
                partition_key="PK",
                sort_key="SK",
            )
        )

    def save_message(self, session_id: str, author: str, content: str, msg_type: str = "message", timestamp: Optional[int] = None):
        ts = timestamp or int(time.time())
        item = {
            "author": author,
            "type": msg_type,
            "content": content,
            "timestamp": ts,
            "message_id": uuid4().hex,
        }
        self.dynamo.put(item, partition_key=f"sessao#{session_id}", sort_key=str(ts))

    def list_messages(self, session_id: str, limit: int = 20) -> List[dict]:
        return self.dynamo.query_all(partition_key=f"sessao#{session_id}")[-limit:]

    def save_summary(self, session_id: str, content: str, last_message_timestamp: int):
        item = {
            "type": "resumo",
            "content": content,
            "last_message_timestamp": last_message_timestamp,
            "updated_at": int(time.time())
        }
        self.dynamo.put(item, partition_key=f"sessao#{session_id}", sort_key="RESUMO")

    def get_summary(self, session_id: str) -> Optional[dict]:
        return self.dynamo.get(partition_key=f"sessao#{session_id}", sort_key="RESUMO")
