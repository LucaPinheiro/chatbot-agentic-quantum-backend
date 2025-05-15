from typing import Optional, Union
from app.helpers.exceptions.exceptions import NotFoundException
from app.models.models import Group
from app.schemas.update_group import UpdateGroupResponse


class GroupRepositoryPostgres:
    def __init__(self, db):
        self.db = db

    def delete_group(self, name: str):
        groups = self.db.query(Group).filter(Group.name == name).all()
        if not groups:
            return {"message": "Nenhum grupo encontrado com esse nome."}

        for group in groups:
            self.db.delete(group)
    
        self.db.commit()
        return {"message": f"Grupo deletado com sucesso."}
    
    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        group = self.db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            return None
        return group
    
    def create_group(self, group = Group) -> Group:
        existing_group = self.db.query(Group).filter(Group.name == group.name).first()
        if existing_group:
            raise NotFoundException("Já existe um grupo com esse nome.")
        
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def update_group(self, group_id: str, name: Optional[str], year_semester: Optional[int], status: Optional[bool], user_id: Optional[str]) -> Union[UpdateGroupResponse, dict]:
        group = self.db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            raise NotFoundException("Grupo não encontrado.")
        if name:  
            group.name = name
        if year_semester is not None:
            group.year_semester = year_semester
        if status is not None:
            group.status = status
        if user_id:
            group.user_id = user_id
        
        self.db.commit()
        self.db.refresh(group)
        return UpdateGroupResponse(
            name=group.name,
            year_semester=group.year_semester,
            status=group.status,
            user_id=group.user_id
        )
