from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id"),
        # Причина пропуска бывает только у отсутствующих.
        CheckConstraint("NOT is_present OR reason IS NULL"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_present: Mapped[bool] = mapped_column(default=True)
    reason: Mapped[str | None] = mapped_column(String(255))  # "болезнь", "уваж."

    lesson: Mapped["Lesson"] = relationship(back_populates="attendance")
    student: Mapped["User"] = relationship(lazy="joined")
