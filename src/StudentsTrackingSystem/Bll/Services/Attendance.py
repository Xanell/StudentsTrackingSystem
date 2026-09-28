from sqlalchemy.orm import Session
from Bll.Schemas.Attendance import AttendanceDetail, AttendanceSave, AttendanceUpdate
from Core.Exceptions import BusinessValidationError, NotFoundError
from Dal.Repositories.Attendance import AttendanceRepository
from Dal.Repositories.Lessons import LessonsRepository
from Dal.Repositories.User import UserRepository

class AttendanceService:
    def __init__(self, session: Session):
        self.attendance_repo = AttendanceRepository(session)
        self.lesson_repo = LessonsRepository(session)
        self.user_repo = UserRepository(session)

    def _to_details(self, records) -> list[AttendanceDetail]:
        result = []
        for record in records:
            result.append(AttendanceDetail.model_validate(record))
        return result

    def save_for_lesson(self, data: AttendanceSave) -> list[AttendanceDetail]:
        """Сохранить отметки всего класса за урок. Повторное сохранение обновляет отметки."""
        lesson = self.lesson_repo.get_by_id(data.lesson_id)
        if lesson is None:
            raise NotFoundError(f"Урок с id={data.lesson_id} не найден")

        marks = {}
        for item in data.items:
            student = self.user_repo.get_by_id(item.student_id)
            if student is None or student.class_id != lesson.class_id:
                raise BusinessValidationError(f"Ученик с id={item.student_id} не учится в классе этого урока")
            marks[item.student_id] = (item.is_present, item.reason)

        records = self.attendance_repo.save_for_lesson(data.lesson_id, marks)
        return self._to_details(records)

    def update_attendance(self, attendance_id: int, data: AttendanceUpdate) -> AttendanceDetail:
        """Исправить одну отметку, например ошибочную «Н»."""
        if self.attendance_repo.get_by_id(attendance_id) is None:
            raise NotFoundError(f"Отметка с id={attendance_id} не найдена")
        record = self.attendance_repo.update_attendance(attendance_id, data.is_present, data.reason)
        return AttendanceDetail.model_validate(record)

    def get_by_lesson(self, lesson_id: int) -> list[AttendanceDetail]:
        return self._to_details(self.attendance_repo.get_by_lesson(lesson_id))
