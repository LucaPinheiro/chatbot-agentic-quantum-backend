import boto3
import base64
from decimal import Decimal
from typing import Dict, Union, Optional, List, Any, Generator
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import json
from contextlib import contextmanager
from dataclasses import dataclass

from app.core.settings import load_settings, StageEnum
from app.schemas.sqs import SQSMessage

settings = load_settings()


class DynamoRepositoryError(RuntimeError):
    """Thin wrapper so the domain never sees botocore exceptions."""


@dataclass(frozen=True, slots=True)
class DynamoConfig:
    table_name: str
    region_name: str = settings.aws_region
    endpoint_url: Optional[str] = None
    partition_key: str = "PK"
    sort_key: str = "SK"
    gsi_partition_key: Optional[str] = None
    gsi_sort_key: Optional[str] = None


class DynamoDBResources:
    def __init__(self, config: Union[DynamoConfig, Dict[str, Any]]):
        if isinstance(config, dict):
            config = DynamoConfig(**config)

        self.cfg = config
        self._session = boto3.Session(region_name=self.cfg.region_name)
        self._client = self._session.client("dynamodb", endpoint_url=self.cfg.endpoint_url)
        self._table = self._session.resource("dynamodb", endpoint_url=self.cfg.endpoint_url).Table(
            self.cfg.table_name
        )
        self._serializer = TypeSerializer()
        self._deserializer = TypeDeserializer()

    @staticmethod
    def _decimalise(obj: Any) -> Any:
        if isinstance(obj, (float, int)):
            return Decimal(str(obj))
        if isinstance(obj, dict):
            return {k: DynamoDBResources._decimalise(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [DynamoDBResources._decimalise(v) for v in obj]
        return obj

    @classmethod
    def _undecimalise(cls, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        if isinstance(obj, dict):
            return {k: cls._undecimalise(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [cls._undecimalise(v) for v in obj]
        return obj

    def put(self, item: Dict[str, Any], partition_key: str, sort_key: Optional[str] = None) -> None:
        try:
            item_copy = dict(item)
            item_copy[self.cfg.partition_key] = partition_key
            if sort_key:
                item_copy[self.cfg.sort_key] = sort_key

            self._table.put_item(Item=self._decimalise(item_copy))
        except ClientError as exc:
            raise DynamoRepositoryError(exc) from exc

    def get(self, partition_key: str, sort_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            key = {self.cfg.partition_key: partition_key}
            if sort_key:
                key[self.cfg.sort_key] = sort_key

            resp = self._table.get_item(Key=key)
            item = resp.get("Item")
            return self._undecimalise(item) if item else None
        except ClientError as exc:
            raise DynamoRepositoryError(exc) from exc

    def update(self, partition_key: str, sort_key: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            placeholders = {f"#k{i}": k for i, k in enumerate(update_dict)}
            values = {f":v{i}": self._decimalise(v) for i, v in enumerate(update_dict.values())}
            update_expr = "SET " + ", ".join(f"{k} = {v}" for k, v in zip(placeholders, values))

            resp = self._table.update_item(
                Key={self.cfg.partition_key: partition_key, self.cfg.sort_key: sort_key},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=placeholders,
                ExpressionAttributeValues=values,
                ReturnValues="ALL_NEW",
            )
            return self._undecimalise(resp["Attributes"])
        except ClientError as exc:
            raise DynamoRepositoryError(exc) from exc

    def delete(self, partition_key: str, sort_key: Optional[str] = None) -> None:
        try:
            key = {self.cfg.partition_key: partition_key}
            if sort_key:
                key[self.cfg.sort_key] = sort_key
            self._table.delete_item(Key=key)
        except ClientError as exc:
            raise DynamoRepositoryError(exc) from exc

    def query_all(self, partition_key: str, begins_with: Optional[str] = None, index_name: Optional[str] = None, **extra_kwargs) -> List[Dict[str, Any]]:
        cond = Key(self.cfg.partition_key).eq(partition_key)
        if begins_with:
            cond &= Key(self.cfg.sort_key).begins_with(begins_with)

        kwargs = {"KeyConditionExpression": cond, **extra_kwargs}
        if index_name:
            kwargs["IndexName"] = index_name

        items: List[Dict[str, Any]] = []
        paginator = self._client.get_paginator("query")
        for page in paginator.paginate(TableName=self.cfg.table_name, **kwargs):
            items.extend(page["Items"])
        return [self._undecimalise(i) for i in items]

    def scan_all(self, **scan_kwargs) -> List[Dict[str, Any]]:
        paginator = self._client.get_paginator("scan")
        items: List[Dict[str, Any]] = []
        for page in paginator.paginate(TableName=self.cfg.table_name, **scan_kwargs):
            items.extend(page["Items"])
        return [self._undecimalise(i) for i in items]

    @contextmanager
    def batch(self) -> Generator["boto3.dynamodb.table.BatchWriter", None, None]:
        try:
            with self._table.batch_writer(overwrite_by_pkeys=[self.cfg.partition_key, self.cfg.sort_key]) as b:
                yield b
        except ClientError as exc:
            raise DynamoRepositoryError(exc) from exc


class SQSResources:
    def __init__(self, region_name: str = settings.aws_region):
        self.sqs = boto3.client("sqs", region_name=region_name)

    def send_message(self, sqs_message: SQSMessage) -> bool:
        try:
            if settings.app_env == StageEnum.test:
                return True
            response = self.sqs.send_message(
                QueueUrl=settings.sqs_queue_url,
                MessageGroupId=sqs_message.message_group_id.name,
                MessageBody=sqs_message.to_json()
            )
            print(f"MessageId: {response.get('MessageId')} was sent to the queue")
            return response.get("MessageId") is not None
        except Exception as e:
            print(e)
            return False


class RekognitionResources:
    def __init__(self, region_name: str = settings.aws_region):
        if settings.app_env != StageEnum.test:
            self.rekognition = boto3.client("rekognition", region_name=region_name)

    def search_face(self, source_image: str) -> Dict[str, Union[bool, str]]:
        if settings.app_env == StageEnum.test:
            return {"match": True}
        try:
            image = base64.b64decode(source_image)
            response = self.rekognition.search_faces_by_image(
                CollectionId=settings.rekognition_collection_id,
                Image={"Bytes": image},
                FaceMatchThreshold=90,
                MaxFaces=1
            )
            if response.get("FaceMatches"):
                user_id = response["FaceMatches"][0]["Face"].get("ExternalImageId")
                if user_id:
                    return {"match": True, "user_id": user_id}
            return {"match": False}
        except Exception as error:
            return {"match": False, "error": str(error)}

    def index_faces(self, image: bytes, citizen_id: str) -> Optional[str]:
        try:
            if settings.app_env == StageEnum.test:
                return "test"
            response = self.rekognition.index_faces(
                CollectionId=settings.rekognition_collection_id,
                Image={"Bytes": image},
                ExternalImageId=citizen_id,
                MaxFaces=1,
            )
            return response.get("FaceRecords", [{}])[0].get("Face", {}).get("FaceId")
        except Exception as e:
            print(e)
            return None

    def delete_faces(self, face_ids: list) -> bool:
        try:
            if settings.app_env == StageEnum.test:
                return True
            response = self.rekognition.delete_faces(
                CollectionId=settings.rekognition_collection_id,
                FaceIds=face_ids
            )
            return response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
        except Exception as e:
            print(e)
            return False


class S3Resources:
    def __init__(self, region_name: str = settings.aws_region):
        self.s3 = boto3.client("s3", region_name=region_name)

    def get_object_link(self, key: str) -> str:
        try:
            if settings.app_env == StageEnum.test:
                return "test"
            url = self.s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.aws_s3_bucket,
                    "Key": key
                },
                ExpiresIn=3600
            )
            return url
        except Exception as e:
            print(e)
            return ""

    def get_object(self, key: str) -> dict:
        try:
            if settings.app_env == StageEnum.test:
                return {"Body": b"test"}
            response = self.s3.get_object(
                Bucket=settings.aws_s3_bucket,
                Key=key
            )
            return response
        except Exception as e:
            print(e)
            return {}

    def put_object(self, key: str, body: bytes) -> bool:
        try:
            if settings.app_env == StageEnum.test:
                return True
            response = self.s3.put_object(
                Bucket=settings.aws_s3_bucket,
                Key=key,
                Body=body
            )
            return response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
        except Exception as e:
            print(e)
            return False

    def list_objects(self) -> list:
        try:
            if settings.app_env == StageEnum.test:
                return []
            response = self.s3.list_objects_v2(Bucket=settings.aws_s3_bucket)
            return response.get("Contents", [])
        except Exception as e:
            print(e)
            return []

    def list_objects_by_prefix(self, prefix: str) -> list:
        try:
            if settings.app_env == StageEnum.test:
                return []
            response = self.s3.list_objects_v2(
                Bucket=settings.aws_s3_bucket,
                Prefix=prefix
            )
            return response.get("Contents", [])
        except Exception as e:
            print(e)
            return []

    def delete_object(self, key: str) -> bool:
        try:
            if settings.app_env == StageEnum.test:
                return True
            response = self.s3.delete_object(
                Bucket=settings.aws_s3_bucket,
                Key=key
            )
            return response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 204
        except Exception as e:
            print(e)
            return False
