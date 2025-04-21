# app/infra/repositories/file_repository_s3.py
from typing import Iterable, Optional

from app.domain.entities.file import File
from app.domain.interfaces.file_repository import IFileRepository
from app.infra.external.aws import S3Resources

class FileRepositoryS3(IFileRepository):

    def __init__(self, s3: S3Resources):
        self._s3 = s3

    # --------------- IFileRepository --------------------

    def upload(self, file: File) -> bool:
        return self._s3.put_object(key=file.key, body=file.content or b"")

    def download(self, key: str) -> Optional[File]:
        obj = self._s3.get_object(key)
        if not obj:
            return None
        return File.from_s3_dict(
            {
                "Key": key,
                "Size": obj["ContentLength"],
                "LastModified": obj["LastModified"],
                "ContentType": obj["ContentType"],
                "Body": obj["Body"].read(),
            }
        )

    def delete(self, key: str) -> bool:
        return self._s3.delete_object(key)

    def list(self, prefix: str | None = None) -> Iterable[File]:
        items = (
            self._s3.list_objects_by_prefix(prefix)
            if prefix
            else self._s3.list_objects()
        )
        return [File.from_s3_dict(i) for i in items]

    def presigned_url(self, key: str, expires: int = 3600) -> str:
        return self._s3.get_object_link(key)
    
    def get_object(self, key: str) -> Optional[File]:
        obj = self._s3.get_object(key)
        if not obj:
            return None
        return File.from_s3_dict(obj)

    
