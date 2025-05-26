from pydantic import BaseModel


class GetClassProgressPercentualByClassRequest(BaseModel):
    class_topics_id: str
    topic_progress_id: str
   
class GetClassProgressPercentualByClassResponse(BaseModel):
    topic_progress_id: str
    class_progress_percentual: str
    total: int
    done: int

