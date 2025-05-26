from typing import List, Union
from pydantic import BaseModel


class DeleteTopicsByIdRequest(BaseModel):
    class_topics_id: Union[str, List[str]]
    class_id: Union[str, List[str]]
    topic: Union[str, List[str]]

class DeleteTopicsByIdResponse(BaseModel):
    message: str