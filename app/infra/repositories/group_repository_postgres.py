from app.models.models import Group


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
