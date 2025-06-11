from typing import List, Optional, Union
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app import schemas
from app.helpers.exceptions.exceptions import NotFoundException
from app.models.models import Group, GroupEnrollment, User
from app.schemas.add_user_group import AddUserGroupResponse
from app.schemas.update_group import UpdateGroupResponse



class GroupRepositoryPostgres:
    def __init__(self, db):
        self.db = db

    def delete_group(self, group_id: str, name: str):
        group = (
            self.db.query(Group)
            .filter(Group.group_id == group_id, Group.name == name)
            .first()
        )

        if not group:
            return {"message": "Grupo não encontrado com esse ID e nome."}
        
        # Primeiro, apagar as inscrições relacionadas
        self.db.query(GroupEnrollment).filter(GroupEnrollment.group_id == group_id).delete()

        self.db.delete(group)
        self.db.commit()

        return {"message": f"Grupo '{name}' deletado com sucesso."}

    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        group = self.db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            return None
        return group
    
    def create_group(self, group: Group, user_ids: Optional[List[str]] = None) -> Group:
        try:
            manager = self.db.query(User).filter(User.user_id == group.manager_id).first()
            if not manager:
                raise HTTPException(status_code=400, detail="Manager_id inválido: professor/admin não existe.")

            existing_group = self.db.query(Group).filter(Group.name == group.name).first()
            if existing_group:
                raise HTTPException(status_code=400, detail="Já existe um grupo com esse nome.")

            # Adiciona o grupo
            self.db.add(group)
            self.db.flush()  # Garante que o group_id está disponível, mas sem fazer commit ainda

            enrollments = []
            
            user_ids = user_ids or []
            for user_id in user_ids:
                user = self.db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise HTTPException(status_code=400, detail=f"Usuário com ID {user_id} não encontrado.")
                if user.permission != 1:
                    raise HTTPException(status_code=403, detail=f"Usuário com ID {user_id} não possui permissão adequada.")
                enrollments.append(
                    GroupEnrollment(group_id=group.group_id, student_id=user_id)
                )

            self.db.bulk_save_objects(enrollments)

            self.db.commit()
            self.db.refresh(group)

            return group

        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


    
    def update_group(self, group_id: str, name: str, year_semester: str, status: bool, manager_id: str):
        group = self.db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            raise ValueError("Grupo não encontrado.")

        group.name = name
        group.year_semester = year_semester
        group.status = status
        group.manager_id = manager_id

        self.db.commit()
        self.db.refresh(group)

        return group

    def update_group_enrollments(self, group_id: str, user_ids: List[str]):
        # Remove relacionamentos antigos
        self.db.query(GroupEnrollment).filter(GroupEnrollment.group_id == group_id).delete(synchronize_session=False)

        # Insere novos relacionamentos
        for user_id in user_ids:
            enrollment = GroupEnrollment(group_id=group_id, student_id=user_id)
            self.db.add(enrollment)

        self.db.commit()

    def is_manager_group(self, group_id: str, user_id: str) -> bool:
        exists = self.db.query(Group).filter(
            Group.group_id == group_id,
            Group.manager_id == user_id
        ).first()
        return exists is not None
    
    def add_user_group(self, user_id: str, group_id: str) -> AddUserGroupResponse:
        # ✅ Verifica se o usuário existe e é um aluno (permission == 1)
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"Usuário {user_id} não encontrado.")
        if user.permission != 1:
            raise HTTPException(
                status_code=403,
                detail=f"Usuário {user_id} não tem permissão de aluno para ser adicionado ao grupo."
            )
         # ✅ Verifica se o grupo existe
        group = self.db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail=f"Grupo {group_id} não encontrado.")

        # ✅ Verifica se o usuário já está no grupo
        existing_enrollment = (
            self.db.query(GroupEnrollment)
            .filter(
                GroupEnrollment.student_id == user_id,
                GroupEnrollment.group_id == group_id
            )
            .first()
        )

        if existing_enrollment:
            raise HTTPException(
                status_code=400,
                detail=f"Usuário {user_id} já está matriculado no grupo {group_id}."
            )

        # ✅ Cria nova matrícula
        new_enrollment = GroupEnrollment(
            group_id=group_id,
            student_id=user_id,
        )

        self.db.add(new_enrollment)
        self.db.commit()

        return AddUserGroupResponse(
            user_id=user_id,
            group_id=group_id,
            message=f"Usuário {user_id} adicionado ao grupo {group_id} com sucesso."
        )
        

    