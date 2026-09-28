from datetime import date
from sqlalchemy.orm import Session
from Bll.Schemas.Mark import MarkDetail, MarkSet
from Core.Enums import RoleName
from Core.Exceptions import BusinessValidationError, NotFoundError
from Dal.Repositories.Lessons import LessonsRepository
from Dal.Repositories.Mark import MarkRepository
from Dal.Repositories.User import UserRepository

def calculate_average(grades: list[int]) -> float | None:
    """Средний балл с точностью до сотых. None — оценок нет."""
    if len(grades) == 0:
        return None
    total = 0
    for grade in grades:
        total += grade
    return round(total / len(grades), 2)

class MarkService:
    def __init__(self, session: Session):
        self.mark_repo = MarkRepository(session)
        self.lesson_repo = LessonsRepository(session)
        self.user_repo = UserRepository(session)

    def _to_details(self, marks) -> list[MarkDetail]:
        result = []
        for mark in marks:
            result.append(MarkDetail.model_validate(mark))
        return result

    def set_mark(self, data: MarkSet) -> MarkDetail:
        """Поставить или изменить оценку в клетке журнала."""
        lesson = self.lesson_repo.get_by_id(data.lesson_id)
        if lesson is None:
            raise NotFoundError(f"Урок с id={data.lesson_id} не найден")

        student = self.user_repo.get_by_id(data.student_id)
        if student is None or student.role != RoleName.STUDENT:
            raise NotFoundError(f"Ученик с id={data.student_id} не найден")
        if student.class_id != lesson.class_id:
            raise BusinessValidationError(f"{student.last_name} не учится в классе этого урока")
        if student.deactivated_at is not None:
            raise BusinessValidationError(f"{student.last_name} выбыл, ставить оценки нельзя")

        mark = self.mark_repo.set_mark(
            lesson_id=data.lesson_id,
            student_id=data.student_id,
            grade_type=data.grade_type,
            grade=data.grade,
        )
        return MarkDetail.model_validate(mark)

    def clear_mark(self, mark_id: int) -> MarkDetail:
        """Очистить клетку: оценку поставили по ошибке."""
        if self.mark_repo.get_by_id(mark_id) is None:
            raise NotFoundError(f"Оценка с id={mark_id} не найдена")
        return MarkDetail.model_validate(self.mark_repo.clear_mark(mark_id))

    def get_by_lesson(self, lesson_id: int) -> list[MarkDetail]:
        return self._to_details(self.mark_repo.get_by_lesson(lesson_id))

    def get_student_marks(
        self, student_id: int, start_date: date, end_date: date, subject_id: int | None = None
    ) -> list[MarkDetail]:
        return self._to_details(
            self.mark_repo.get_by_student_and_period(student_id, start_date, end_date, subject_id)
        )

    def get_average(self, student_id: int, start_date: date, end_date: date, subject_id: int) -> float | None:
        """Средний балл ученика по предмету за период (например, за четверть)."""
        grades = []
        for mark in self.mark_repo.get_by_student_and_period(student_id, start_date, end_date, subject_id):
            grades.append(mark.grade)
        return calculate_average(grades)
