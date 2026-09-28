from datetime import date
from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Core.Enums import MAX_LESSONS_PER_DAY
from .Base import Base

class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("class_id", "lesson_date", "lesson_number"),
        CheckConstraint(f"lesson_number BETWEEN 1 AND {MAX_LESSONS_PER_DAY}"),
        CheckConstraint("homework_due_date IS NULL OR homework_due_date >= lesson_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_date: Mapped[date] = mapped_column(Date)
    lesson_number: Mapped[int] = mapped_column(SmallInteger)
    topic: Mapped[str | None] = mapped_column(String(255))
    homework: Mapped[str | None] = mapped_column(Text)
    homework_due_date: Mapped[date | None] = mapped_column(Date)  # None — к следующему уроку

    school_class: Mapped["SchoolClass"] = relationship(lazy="joined")
    subject: Mapped["Subject"] = relationship(lazy="joined")
    teacher: Mapped["User"] = relationship(lazy="joined")

    # Только прикреплённые материалы. Откреплённые остаются в базе, но сюда не попадают.
    # viewonly: файлы добавляются и открепляются через LessonFileRepository, а не через этот список.
    files: Mapped[list["LessonFile"]] = relationship(
        primaryjoin="and_(Lesson.id == LessonFile.lesson_id, LessonFile.detached_at.is_(None))",
        order_by="LessonFile.uploaded_at",
        viewonly=True,
    )
    submissions: Mapped[list["HomeworkSubmission"]] = relationship(
        back_populates="lesson", order_by="HomeworkSubmission.submitted_at",
    )
    marks: Mapped[list["Mark"]] = relationship(back_populates="lesson")
    attendance: Mapped[list["Attendance"]] = relationship(back_populates="lesson")
