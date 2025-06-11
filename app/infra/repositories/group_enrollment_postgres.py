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

