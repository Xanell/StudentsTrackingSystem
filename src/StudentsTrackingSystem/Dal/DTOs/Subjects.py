from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .Base import Base

class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)  # "Математика"
    short_name: Mapped[str | None] = mapped_column(String(10))   # "Матем."
