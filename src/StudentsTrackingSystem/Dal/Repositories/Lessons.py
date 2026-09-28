from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..DTOs.Lessons import Lesson
from .Common import UNSET, apply_updates

class LessonsRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_lesson(self, class_id: int, subject_id: int, teacher_id: int, lesson_date: date, lesson_number: int, topic: str | None = None, homework: str | None = None, homework_due_date: date | None = None) -> Lesson:
        lesson = Lesson(
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            lesson_date=lesson_date,
            lesson_number=lesson_number,
            topic=topic,
            homework=homework,
            homework_due_date=homework_due_date,
        )
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def get_by_id(self, lesson_id: int) -> Lesson | None:
        return self.db.get(Lesson, lesson_id)

    def get_by_class_date_number(self, class_id: int, lesson_date: date, lesson_number: int) -> Lesson | None:
        """Для get-or-create урока по расписанию и проверки на дубль."""
        stmt = select(Lesson).where(
            Lesson.class_id == class_id,
            Lesson.lesson_date == lesson_date,
            Lesson.lesson_number == lesson_number,
        )
        return self.db.scalars(stmt).one_or_none()

    def get_by_class_and_date(self, class_id: int, lesson_date: date) -> list[Lesson]:
        stmt = (
            select(Lesson)
            .where(Lesson.class_id == class_id, Lesson.lesson_date == lesson_date)
            .order_by(Lesson.lesson_number)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_class_and_period(self, class_id: int, start_date: date, end_date: date, subject_id: int | None = None) -> list[Lesson]:
        """
        Уроки класса за период.
        - дневник ученика на неделю: без subject_id;
        - журнал учителя за четверть: с subject_id.
        """
        stmt = select(Lesson).where(
            Lesson.class_id == class_id,
            Lesson.lesson_date >= start_date,
            Lesson.lesson_date <= end_date,
        )
        if subject_id is not None:
            stmt = stmt.where(Lesson.subject_id == subject_id)
        stmt = stmt.order_by(Lesson.lesson_date, Lesson.lesson_number)
        return list(self.db.scalars(stmt).all())

    def get_by_teacher_and_date(self, teacher_id: int, lesson_date: date) -> list[Lesson]:
        """Уроки учителя за день — главная страница учителя."""
        stmt = (
            select(Lesson)
            .where(Lesson.teacher_id == teacher_id, Lesson.lesson_date == lesson_date)
            .order_by(Lesson.lesson_number)
        )
        return list(self.db.scalars(stmt).all())

    def get_with_homework(self, class_id: int, start_date: date, end_date: date) -> list[Lesson]:
        """Уроки класса за период, на которых задали домашку."""
        stmt = (
            select(Lesson)
            .where(
                Lesson.class_id == class_id,
                Lesson.lesson_date >= start_date,
                Lesson.lesson_date <= end_date,
                Lesson.homework.is_not(None),
            )
            .order_by(Lesson.lesson_date, Lesson.lesson_number)
        )
        return list(self.db.scalars(stmt).all())

    def update_lesson(self, lesson_id: int, subject_id: int = UNSET, teacher_id: int = UNSET, topic: str | None = UNSET, homework: str | None = UNSET, homework_due_date: date | None = UNSET) -> Lesson | None:
        lesson = self.get_by_id(lesson_id)
        if lesson is None:
            return None
        apply_updates(
            lesson,
            subject_id=subject_id,
            teacher_id=teacher_id,
            topic=topic,
            homework=homework,
            homework_due_date=homework_due_date,
        )
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    # delete_lesson нет: проведённые уроки не удаляются.
