from sqlalchemy.orm import Session
from Bll.Schemas.LessonFile import LessonFileDetail
from Bll.Services.FileStorage import get_absolute_path, save_file
from Core.Exceptions import NotFoundError
from Dal.Repositories.LessonFile import LessonFileRepository
from Dal.Repositories.Lessons import LessonsRepository

class LessonFileService:
    def __init__(self, session: Session):
        self.lesson_file_repo = LessonFileRepository(session)
        self.lesson_repo = LessonsRepository(session)

    def _get_attached(self, file_id: int):
        lesson_file = self.lesson_file_repo.get_by_id(file_id)
        if lesson_file is None or lesson_file.detached_at is not None:
            raise NotFoundError(f"Материал с id={file_id} не найден")
        return lesson_file

    def attach_file(self, lesson_id: int, uploaded_file) -> LessonFileDetail:
        """uploaded_file — файл из request.FILES."""
        if self.lesson_repo.get_by_id(lesson_id) is None:
            raise NotFoundError(f"Урок с id={lesson_id} не найден")
        file_path, original_name = save_file(uploaded_file, "lessons")
        lesson_file = self.lesson_file_repo.create_file(lesson_id, file_path, original_name)
        return LessonFileDetail.model_validate(lesson_file)

    def detach_file(self, file_id: int) -> LessonFileDetail:
        self._get_attached(file_id)
        return LessonFileDetail.model_validate(self.lesson_file_repo.detach_file(file_id))

    def get_by_lesson(self, lesson_id: int) -> list[LessonFileDetail]:
        result = []
        for lesson_file in self.lesson_file_repo.get_by_lesson(lesson_id):
            result.append(LessonFileDetail.model_validate(lesson_file))
        return result

    def get_for_download(self, file_id: int) -> tuple[str, str]:
        """(полный путь к файлу, исходное имя) — для FileResponse(..., filename=исходное_имя)."""
        lesson_file = self._get_attached(file_id)
        return get_absolute_path(lesson_file.file_path), lesson_file.original_name
