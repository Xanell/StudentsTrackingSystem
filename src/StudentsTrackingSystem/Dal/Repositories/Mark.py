from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from Core.Enums import GradeType
from ..DTOs.Lessons import Lesson
from ..DTOs.Mark import Mark

class MarkRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_by_id(self, mark_id: int) -> Mark | None:
        return self.db.get(Mark, mark_id)

    def get_cell(self, lesson_id: int, student_id: int, grade_type: GradeType) -> Mark | None:
        stmt = select(Mark).where(
            Mark.lesson_id == lesson_id,
            Mark.student_id == student_id,
            Mark.grade_type == grade_type,
        )
        return self.db.scalars(stmt).one_or_none()

    def set_mark(self, lesson_id: int, student_id: int, grade_type: GradeType, grade: int) -> Mark:
        mark = self.get_cell(lesson_id, student_id, grade_type)
        if mark is None:
            mark = Mark(
                lesson_id=lesson_id,
                student_id=student_id,
                grade_type=grade_type,
                grade=grade,
            )
            self.db.add(mark)
        else:
            mark.grade = grade
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def clear_mark(self, mark_id: int) -> Mark | None:
        mark = self.get_by_id(mark_id)
        if mark is None:
            return None
        mark.grade = None
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def get_by_lesson(self, lesson_id: int, include_cleared: bool = False) -> list[Mark]:
        stmt = select(Mark).where(Mark.lesson_id == lesson_id)
        if not include_cleared:
            stmt = stmt.where(Mark.grade.is_not(None))
        return list(self.db.scalars(stmt).all())

    def get_by_lesson_ids(self, lesson_ids: list[int], include_cleared: bool = False) -> list[Mark]:
        if not lesson_ids:
            return []
        stmt = select(Mark).where(Mark.lesson_id.in_(lesson_ids))
        if not include_cleared:
            stmt = stmt.where(Mark.grade.is_not(None))
        return list(self.db.scalars(stmt).all())

    def get_by_student_and_period(self, student_id: int, start_date: date, end_date: date, subject_id: int | None = None) -> list[Mark]:
        stmt = (
            select(Mark)
            .join(Lesson, Mark.lesson_id == Lesson.id)
            .where(
                Mark.student_id == student_id,
                Mark.grade.is_not(None),
                Lesson.lesson_date >= start_date,
                Lesson.lesson_date <= end_date,
            )
            .options(joinedload(Mark.lesson))
            .order_by(Lesson.lesson_date, Lesson.lesson_number)
        )
        if subject_id is not None:
            stmt = stmt.where(Lesson.subject_id == subject_id)
        return list(self.db.scalars(stmt).all())