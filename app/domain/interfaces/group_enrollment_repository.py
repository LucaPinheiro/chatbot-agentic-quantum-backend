from abc import ABC, abstractmethod


class IGroupEnrollmentRepository(ABC):
  
  @abstractmethod
  def is_student(self, group_id: str, student_id: str) -> bool:
    """
    Verifica se o aluno pertence ao grupo
    """
    pass
  