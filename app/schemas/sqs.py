import json
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional
from datetime import datetime


class SQSMessage(BaseModel):
    session_id: str
    summary_cutoff: Optional[str]
    message_group_id: Optional[Literal["summarization"]]
    class_id: Optional[str]
    topics: Optional[List[Dict[str, str]]]

    def to_json(self) -> str:
        return self.model_dump_json()


class SQSEvent:
    def __init__(self, raw_event: dict):
        self.records = [json.loads(r["body"]) for r in raw_event["Records"]]

    def __iter__(self):
        return iter(self.records)
