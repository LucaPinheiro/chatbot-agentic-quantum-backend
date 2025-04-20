from sqlalchemy import create_engine
from app.core.settings import load_settings
from app.models.models import Base

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
    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")


if __name__ == "__main__":
    create_db_tables()
