from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class SchoolClass(Base):
    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint("school_year_id", "number", "letter"),
        CheckConstraint("number BETWEEN 1 AND 11"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(SmallInteger)  # 5
    letter: Mapped[str] = mapped_column(String(1))     # "А"
    school_year_id: Mapped[int] = mapped_column(ForeignKey("school_years.id"))

    school_year: Mapped["SchoolYear"] = relationship(back_populates="school_classes", lazy="joined")
    students: Mapped[list["User"]] = relationship(
        back_populates="school_class",
        order_by="[User.last_name, User.first_name]",
    )
