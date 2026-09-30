from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Core.Enums import RoleName
from .Base import Base, str_enum

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str] = mapped_column(String(50))
    role: Mapped[RoleName] = mapped_column(str_enum(RoleName, "role"))
    # Заполняется только у учеников
    class_id: Mapped[int | None] = mapped_column(ForeignKey("classes.id"))
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    school_class: Mapped["SchoolClass | None"] = relationship(back_populates="students", lazy="joined")
