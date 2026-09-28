from sqlalchemy import text
import Dal.DTOs  # noqa: F401 — регистрирует все модели в Base.metadata
from Core.Seed import admin_seed
from Dal.database import SessionLocal, engine
from Dal.DTOs.Base import Base

def check_connection():
    with engine.connect() as conn:
        row = conn.execute(text("select current_database(), current_user, version()")).one()
        print(row)

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы.")

def reset_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Таблицы пересозданы.")

if __name__ == "__main__":
    check_connection()
    reset_tables()

    with SessionLocal() as session:
        admin_seed(session)
