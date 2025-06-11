from abc import ABC, abstractmethod
from typing import List

from app.models.models import GroupEnrollment


class IGroupEnrollmentRepository(ABC):
  
  @abstractmethod
  def is_student(self, group_id: str, student_id: str) -> bool:
    """
    Verifica se o aluno pertence ao grupo
    """
    pass
  
  @abstractmethod
  def get_all_students_by_group_id(self, group_id: str) -> list:
    """
    Retorna todos os alunos matriculados no grupo
    """
    pass
  def get_enrollment_by_student_id(self, student_id: str) -> GroupEnrollment | None:
        pass
  def delete_user_from_group(self, user_id: str) -> object:
        """
        Remove um usuário do grupo
        """
        pass
  def add_user_group(self, user_id: List[str], group_id: str) -> GroupEnrollment:
        pass