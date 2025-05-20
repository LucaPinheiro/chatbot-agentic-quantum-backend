from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from datetime import datetime
from app.core.settings import load_settings
from app.models.models import Base, User, Group, ClassModel, GroupEnrollment, Session as UserSession
from app.helpers.utils.encrypt import Encrypt


def create_db_tables():
    """Create database tables using SQLAlchemy."""
    settings = load_settings()

    try:
        engine = create_engine(settings.postgres_url)

        print(f"Conectando ao banco de dados em: {settings.postgres_url}")
        print("Tabelas registradas no Base.metadata:", Base.metadata.tables.keys())

        # Drop and recreate tables
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        print("Tabelas criadas com sucesso.")

        # ─── Criar dados iniciais ─── #
        with SQLAlchemySession(engine) as session:
            admin_exists = session.query(User).filter_by(email="admin@example.com").first()
            if not admin_exists:
                now = datetime.now()

                admin = User(
                    user_id="admin-id-001",
                    name="Admin Teste",
                    email="admin@example.com",
                    password=Encrypt.hash_password("admin123"),
                    created_at=now,
                    permission=3
                )
                session.add(admin)

                professor = User(
                    user_id="professor-id-001",
                    name="Professor Teste",
                    email="professor@example.com",
                    password=Encrypt.hash_password("professor123"),
                    created_at=now,
                    permission=2
                )
                session.add(professor)

                aluno = User(
                    user_id="aluno-id-001",
                    name="Aluno Teste",
                    email="aluno@example.com",
                    password=Encrypt.hash_password("aluno123"),
                    created_at=now,
                    permission=1
                )
                session.add(aluno)

                # Criar Group
                group = Group(
                    group_id="group-id-001",
                    name="Grupo Python Básico",
                    year_semester=202501,
                    status=True,
                    manager_id=professor.user_id
                )
                session.add(group)

                # Criar ClassModel associada ao Group
                class_ = ClassModel(
                    class_id="class-id-001",
                    group_id=group.group_id,
                    title="Introdução ao Python",
                    pdf_url="https://example.com/python_intro.pdf",
                    status=True,
                    last_access_class=now,
                    created_at=now,
                    order=1
                )
                session.add(class_)

                # Matricular o aluno no Group
                enrollment = GroupEnrollment(
                    group_id=group.group_id,
                    student_id=aluno.user_id
                )
                session.add(enrollment)

                # Criar uma Session do aluno acessando essa aula
                session_model = UserSession(
                    session_id="abcd",
                    user_id=aluno.user_id,
                    class_id=class_.class_id,
                    group_id=group.group_id,
                    created_at=now
                )
                session.add(session_model)

                session.commit()
                print("Usuários e entidades relacionadas criados com sucesso.")
                # Verificação: listar usuários, grupos, classes, etc.
                print("\n--- VERIFICAÇÃO DOS DADOS INSERIDOS ---")
                print("Usuários:")
                for user in session.query(User).all():
                    print(f" - {user.user_id} | {user.name} | {user.email} | Permissão: {user.permission}")

                print("\nGrupos:")
                for g in session.query(Group).all():
                    print(f" - {g.group_id} | {g.name} | Gerente: {g.manager_id}")

                print("\nAulas (Classes):")
                for c in session.query(ClassModel).all():
                    print(f" - {c.class_id} | {c.title} | Grupo: {c.group_id}")

                print("\nMatrículas:")
                for e in session.query(GroupEnrollment).all():
                    print(f" - Aluno: {e.student_id} | Grupo: {e.group_id}")

                print("\nSessões:")
                for s in session.query(UserSession).all():
                    print(f" - Sessão: {s.session_id} | Aluno: {s.user_id} | Aula: {s.class_id}")

            else:
                print("Usuário admin já existe.")

    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")


if __name__ == "__main__":
    create_db_tables()
