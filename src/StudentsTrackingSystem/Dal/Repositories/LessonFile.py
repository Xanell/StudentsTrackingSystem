from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..DTOs.LessonFile import LessonFile

class LessonFileRepository:

    def __init__(self, session: Session):
        self.db = session

    def create_file(self, lesson_id: int, file_path: str, original_name: str) -> LessonFile:
        lesson_file = LessonFile(lesson_id=lesson_id, file_path=file_path, original_name=original_name)
        self.db.add(lesson_file)
        self.db.commit()
        self.db.refresh(lesson_file)
        return lesson_file

    def get_by_id(self, file_id: int) -> LessonFile | None:
        return self.db.get(LessonFile, file_id)

    def get_by_lesson(self, lesson_id: int, include_detached: bool = False) -> list[LessonFile]:
        stmt = select(LessonFile).where(LessonFile.lesson_id == lesson_id)
        if not include_detached:
            stmt = stmt.where(LessonFile.detached_at.is_(None))
        stmt = stmt.order_by(LessonFile.uploaded_at)
        return list(self.db.scalars(stmt).all())

    def detach_file(self, file_id: int) -> LessonFile | None:
        """Открепить материал от урока: прикрепили не тот файл."""
        lesson_file = self.get_by_id(file_id)
        if lesson_file is None:
            return None
        if lesson_file.detached_at is None:
            lesson_file.detached_at = func.now()
            self.db.commit()
            self.db.refresh(lesson_file)
        return lesson_file

    # Удаления нет: материалы уроков не удаляются, только открепляются.
