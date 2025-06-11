from abc import ABC, abstractmethod


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
  