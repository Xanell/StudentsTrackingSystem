from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Core.Enums import GradeType
from .Base import Base, str_enum

class Mark(Base):
    __tablename__ = "marks"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id", "grade_type"),
        CheckConstraint("grade IS NULL OR grade BETWEEN 1 AND 5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    grade: Mapped[int | None] = mapped_column(SmallInteger)  # None — клетка очищена
    grade_type: Mapped[GradeType] = mapped_column(str_enum(GradeType, "grade_type"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lesson: Mapped["Lesson"] = relationship(back_populates="marks")
    student: Mapped["User"] = relationship(lazy="joined")
