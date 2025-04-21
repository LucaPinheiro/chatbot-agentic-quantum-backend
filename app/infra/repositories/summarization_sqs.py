import time
from typing import Optional
from app.infra.external.aws import SQSResources
from app.schemas.sqs import SQSMessage


class SummarizationQueue:
    def __init__(self):
        self.sqs = SQSResources()

    def trigger_summary(self, session_id: str, message_count: int, trigger_timestamp: Optional[int] = None) -> bool:
        payload = {
            "session_id": session_id,
            "message_count": message_count,
            "trigger_timestamp": trigger_timestamp or int(time.time()),
        }
        msg = SQSMessage(payload)
        return self.sqs.send_message(msg)
