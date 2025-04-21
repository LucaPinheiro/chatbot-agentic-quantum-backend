import json
from pydantic import BaseModel
from typing import Dict, Any


class SQSEvent:
    def __init__(self, body: Dict[str, Any]):
        self.body = json.loads(body["Records"][0]["body"])

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def to_dict(self) -> dict:
        return self.__dict__


class SQSMessage(BaseModel):
    message_id: str
    message_body: str

    def to_json(self) -> str:
        return self.model_dump_json()

