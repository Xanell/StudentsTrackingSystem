from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_present: Mapped[bool] = mapped_column(default=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="attendance")
    student: Mapped["User"] = relationship(lazy="joined")
