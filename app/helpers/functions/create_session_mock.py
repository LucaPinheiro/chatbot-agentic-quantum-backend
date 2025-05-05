from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.settings import load_settings
from app.models.models import Base  # ajuste o nome se estiver diferente
from app.models.models import Session as SessionModel  # ajuste o nome se estiver diferente

def create_db_tables():
    """Create sessions table using SQLAlchemy and insert test session."""
    settings = load_settings()

    try:
        engine = create_engine(settings.postgres_url)

        print(f"Conectando ao banco de dados em: {settings.postgres_url}")
        print("Tabelas registradas no Base.metadata:", Base.metadata.tables.keys())

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        print("Tabelas criadas com sucesso.")

        # ─── Criar sessão de teste ─── #
        with Session(engine) as session:
            session_exists = session.query(SessionModel).filter_by(session_id="session#1234").first()
            if not session_exists:
                new_session = SessionModel(
                    session_id="session#1234",
                    user_id="admin-id-001",
                    class_id="c2",
                    group_id="g3",
                    created_at=datetime.utcnow()
                )
                session.add(new_session)
                session.commit()
                print("Sessão de teste criada com sucesso.")
            else:
                print("Sessão de teste já existe.")

    except Exception as e:
        print(f"Ocorreu um erro ao criar a tabela de sessões: {e}")


if __name__ == "__main__":
    create_db_tables()
