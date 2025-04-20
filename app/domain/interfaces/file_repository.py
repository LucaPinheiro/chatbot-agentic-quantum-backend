# app/domain/interfaces/file_repository.py
from abc import ABC, abstractmethod
from typing import Iterable, Optional
from app.domain.entities.file import File


class IFileRepository(ABC):
    @abstractmethod
    def upload(self, file: File) -> bool:         
        pass
              
    @abstractmethod
    def download(self, key: str) -> Optional[File]:   
        pass
      
    @abstractmethod
    def delete(self, key: str) -> bool:           
        pass      
    @abstractmethod
    def list(self, prefix: str | None = None) -> Iterable[File]:
        pass
    @abstractmethod
    def presigned_url(self, key: str, expires: int = 3600) -> str: 
        pass
    
    @abstractmethod
    def get_object(self, key: str) -> Optional[File]:
        pass
    
    
