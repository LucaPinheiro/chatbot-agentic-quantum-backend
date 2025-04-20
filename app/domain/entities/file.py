from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
class File:
    key: str                      
    content: Optional[bytes] = None  
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_s3_dict(cls, d: dict) -> "File":
        return cls(
            key=d["Key"],
            size=d.get("Size"),
            created_at=d.get("LastModified"),
            content_type=d.get("ContentType"),
            content=d.get("Body")
        )
