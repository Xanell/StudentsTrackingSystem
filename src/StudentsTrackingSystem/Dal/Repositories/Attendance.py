from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..DTOs.Attendance import Attendance
from ..DTOs.Lessons import Lesson

class AttendanceRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_by_id(self, attendance_id: int) -> Attendance | None:
        return self.db.get(Attendance, attendance_id)

    def get_by_lesson(self, lesson_id: int) -> list[Attendance]:
        stmt = select(Attendance).where(Attendance.lesson_id == lesson_id)
        return list(self.db.scalars(stmt).all())

    def get_by_lesson_and_student(self, lesson_id: int, student_id: int) -> Attendance | None:
        stmt = select(Attendance).where(Attendance.lesson_id == lesson_id, Attendance.student_id == student_id)
        return self.db.scalars(stmt).one_or_none()

    def save_for_lesson(self, lesson_id: int, marks: dict[int, bool]) -> list[Attendance]:
        existing = {}
        for record in self.get_by_lesson(lesson_id):
            existing[record.student_id] = record
        for student_id, is_present in marks.items():
            record = existing.get(student_id)
            if record is None:
                record = Attendance(lesson_id=lesson_id, student_id=student_id, is_present=is_present)
                self.db.add(record)
                existing[student_id] = record
            else:
                record.is_present = is_present
        self.db.commit()
        return list(existing.values())

    def update_attendance(self, attendance_id: int, is_present: bool) -> Attendance | None:
        record = self.get_by_id(attendance_id)
        if record is None:
            return None
        record.is_present = is_present
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_lesson_ids(self, lesson_ids: list[int]) -> list[Attendance]:
        if not lesson_ids:
            return []
        stmt = select(Attendance).where(Attendance.lesson_id.in_(lesson_ids))
        return list(self.db.scalars(stmt).all())

    def get_absences_by_student_and_period(self, student_id: int, start_date: date, end_date: date) -> list[Attendance]:
        stmt = (
            select(Attendance)
            .join(Lesson, Attendance.lesson_id == Lesson.id)
            .where(
                Attendance.student_id == student_id,
                Attendance.is_present.is_(False),
                Lesson.lesson_date >= start_date,
                Lesson.lesson_date <= end_date,
            )
            .options(joinedload(Attendance.lesson))
            .order_by(Lesson.lesson_date, Lesson.lesson_number)
        )
        return list(self.db.scalars(stmt).all())