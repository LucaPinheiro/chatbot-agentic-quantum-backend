from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.settings import load_settings
from app.models.models import Base, User  # ← Modelo ORM
from app.helpers.utils.encrypt import Encrypt  # ← Para hashear a senha

def create_db_tables():
    """Create database tables using SQLAlchemy."""
    settings = load_settings()

    try:
        engine = create_engine(settings.postgres_url)

        print(f"Conectando ao banco de dados em: {settings.postgres_url}")
        print("Tabelas registradas no Base.metadata:", Base.metadata.tables.keys())

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        print("Tabelas criadas com sucesso.")

        # ─── Criar admin de teste ─── #
        with Session(engine) as session:
            admin_exists = session.query(User).filter_by(email="admin@example.com").first()
            if not admin_exists:
                admin = User(
                    user_id="admin-id-001",
                    name="Admin Teste",
                    email="admin@example.com",
                    password=Encrypt.hash_password("admin123"),  
                    created_at=datetime.now(),
                    permission=3
                )
                session.add(admin)
                session.commit()
                print("Usuário admin criado com sucesso.")
            else:
                print("Usuário admin já existe.")

    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")


if __name__ == "__main__":
    create_db_tables()
