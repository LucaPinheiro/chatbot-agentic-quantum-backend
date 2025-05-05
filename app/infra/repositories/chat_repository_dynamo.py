import datetime
from typing import List, Optional

from app.domain.entities.chat_message import ChatMessage
from app.domain.interfaces.chat_repository import IChatRepository
from app.infra.external.aws import DynamoDBResources

class ChatRepositoryDynamo(IChatRepository):
    def __init__(self, dynamo: DynamoDBResources):
        self.dynamo = dynamo

    def save_message(self, message: ChatMessage) -> None:
        self.dynamo.put(
            item=message.to_dict(),
            partition_key=message.pk,
            sort_key=message.sk
        )

    def get_session_message_history(self, session_id: str) -> List[ChatMessage]:
        raw_items = self.dynamo.query_all(f"session#{session_id}")
        return [
            ChatMessage(
                session_id=session_id,
                timestamp=datetime.datetime.fromisoformat(item["SK"]),
                role=item["role"],
                message=item["message"],
                tokens=item["tokens"],
                user_id=item["user_id"],
                class_id=item["class_id"],
                group_id=item["group_id"]
            )
            for item in raw_items
            if item.get("type", "message") == "message"
        ]

    def save_summary(self, session_id: str, summary: str) -> None:
        self.dynamo.put(
            item={
                "type": "summary",
                "summary": summary,
                "created_at": datetime.datetime.now().isoformat()
            },
            partition_key=f"session#{session_id}",
            sort_key="summary"
        )

    def get_summary(self, session_id: str) -> Optional[str]:
        item = self.dynamo.get(partition_key=f"session#{session_id}", sort_key="summary")
        return item.get("summary") if item else None

    def get_timestamp_from_last_summary(self, session_id: str) -> Optional[str]:
        item = self.dynamo.get(
            partition_key=f"session#{session_id}",
            sort_key="summary"
        )
        if item and "timestamp" in item:
            return item["timestamp"]
        return None
