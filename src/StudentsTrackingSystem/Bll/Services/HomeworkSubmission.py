from sqlalchemy.orm import Session
from Bll.Schemas.HomeworkSubmission import HomeworkSubmissionCreate, HomeworkSubmissionDetail
from Bll.Services.FileStorage import get_absolute_path, save_file
from Core.Enums import RoleName
from Core.Exceptions import BusinessValidationError, NotFoundError, PermissionDeniedError
from Dal.Repositories.HomeworkSubmission import HomeworkSubmissionRepository
from Dal.Repositories.Lessons import LessonsRepository
from Dal.Repositories.User import UserRepository

class HomeworkSubmissionService:
    def __init__(self, session: Session):
        self.submission_repo = HomeworkSubmissionRepository(session)
        self.lesson_repo = LessonsRepository(session)
        self.user_repo = UserRepository(session)

    def _get_submission(self, submission_id: int):
        submission = self.submission_repo.get_by_id(submission_id)
        if submission is None:
            raise NotFoundError(f"Сдача с id={submission_id} не найдена")
        return submission

    def submit(self, student_id: int, data: HomeworkSubmissionCreate, uploaded_file) -> HomeworkSubmissionDetail:
        """
        Сдать домашку. student_id — текущий пользователь, uploaded_file — файл из request.FILES.
        Повторная сдача создаёт новую запись, предыдущие остаются в истории.
        """
        lesson = self.lesson_repo.get_by_id(data.lesson_id)
        if lesson is None:
            raise NotFoundError(f"Урок с id={data.lesson_id} не найден")
        if lesson.homework is None:
            raise BusinessValidationError("На этом уроке не задано домашнее задание")

        student = self.user_repo.get_by_id(student_id)
        if student is None or student.role != RoleName.STUDENT:
            raise PermissionDeniedError("Сдавать домашку может только ученик")
        if student.class_id != lesson.class_id:
            raise PermissionDeniedError("Это задание другого класса")

        file_path, original_name = save_file(uploaded_file, "homework")
        submission = self.submission_repo.create_submission(
            lesson_id=data.lesson_id,
            student_id=student_id,
            file_path=file_path,
            original_name=original_name,
            comment=data.comment,
        )
        return HomeworkSubmissionDetail.model_validate(submission)

    def get_latest(self, lesson_id: int, student_id: int) -> HomeworkSubmissionDetail | None:
        submission = self.submission_repo.get_latest(lesson_id, student_id)
        if submission is None:
            return None
        return HomeworkSubmissionDetail.model_validate(submission)

    def get_latest_by_lesson(self, lesson_id: int) -> list[HomeworkSubmissionDetail]:
        """Действующие сдачи по заданию — по одной, последней, от каждого ученика. Для проверки учителем."""
        latest_by_student = {}
        for submission in self.submission_repo.get_by_lesson(lesson_id):
            # Сдачи идут от старых к новым, поэтому последняя перезапишет предыдущие.
            latest_by_student[submission.student_id] = submission

        result = []
        for submission in latest_by_student.values():
            result.append(HomeworkSubmissionDetail.model_validate(submission))
        return result

    def get_for_download(self, submission_id: int) -> tuple[str, str]:
        """(полный путь к файлу, исходное имя) — для FileResponse(..., filename=исходное_имя)."""
        submission = self._get_submission(submission_id)
        return get_absolute_path(submission.file_path), submission.original_name
