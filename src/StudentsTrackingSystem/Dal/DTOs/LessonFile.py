from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class LessonFile(Base):
    __tablename__ = "lesson_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    file_path: Mapped[str] = mapped_column(String(255))      # "lessons/3f2a…c1.pdf"
    original_name: Mapped[str] = mapped_column(String(255))  # "Дроби_презентация.pdf"
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    detached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # None — прикреплён

    lesson: Mapped["Lesson"] = relationship()
