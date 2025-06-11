from typing import List
from app.models.models import GroupEnrollment


class GroupEnrollmentPostgres:
    def __init__(self, db):
        self.db = db
    
    def is_student(self, group_id: str, student_id: str) -> bool:
      print("repo")
      exists = self.db.query(GroupEnrollment).filter(
          GroupEnrollment.group_id == group_id,
          GroupEnrollment.student_id == student_id
      ).first()
      return exists is not None
  
    def get_all_students_by_group_id(self, group_id: str) -> list:
        students = self.db.query(GroupEnrollment).filter(
            GroupEnrollment.group_id == group_id
        ).all()
        return [student.student_id for student in students]
    
    def get_enrollment_by_student_id(self, student_id: str) -> GroupEnrollment | None:
        return self.db.query(GroupEnrollment).filter(GroupEnrollment.student_id == student_id).first()

    def delete_user_from_group(self, user_id: str) -> None:
        self.db.query(GroupEnrollment).filter(
            GroupEnrollment.student_id == user_id
        ).delete()
        self.db.commit()
        return {"message": "User removed from group successfully"}
    
    def add_user_group(self, users_id: List[str], group_id: str) -> List[GroupEnrollment]:
        new_enrollments = []

        for user_id in users_id:
            # Verifica se a inscrição já existe para evitar duplicatas
            existing = self.db.query(GroupEnrollment).filter_by(student_id=users_id, group_id=group_id).first()
            if existing:
                continue  # já está inscrito, pula

            enrollment = GroupEnrollment(
                student_id=user_id,
                group_id=group_id
            )
            self.db.add(enrollment)
            new_enrollments.append(enrollment)

        self.db.commit()
        return new_enrollments


