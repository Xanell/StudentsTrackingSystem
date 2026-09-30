from sqlalchemy import select
from sqlalchemy.orm import Session
from ..DTOs.Schedule import Schedule
from ..DTOs.SchoolClasses import SchoolClass
from .Common import UNSET, apply_updates

class ScheduleRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_schedule(self, class_id: int, subject_id: int, teacher_id: int, weekday: int, lesson_number: int, room: str | None = None) -> Schedule:
        slot = Schedule(
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            weekday=weekday,
            lesson_number=lesson_number,
            room=room,
        )
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def get_schedule_by_id(self, schedule_id: int) -> Schedule | None:
        return self.db.get(Schedule, schedule_id)

    def get_by_class(self, class_id: int) -> list[Schedule]:
        stmt = (
            select(Schedule)
            .where(Schedule.class_id == class_id)
            .order_by(Schedule.weekday, Schedule.lesson_number)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_class_and_weekday(self, class_id: int, weekday: int) -> list[Schedule]:
        stmt = (
            select(Schedule)
            .where(Schedule.class_id == class_id, Schedule.weekday == weekday)
            .order_by(Schedule.lesson_number)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_class_slot(self, class_id: int, weekday: int, lesson_number: int) -> Schedule | None:
        stmt = select(Schedule).where(
            Schedule.class_id == class_id,
            Schedule.weekday == weekday,
            Schedule.lesson_number == lesson_number,
        )
        return self.db.scalars(stmt).one_or_none()

    def get_teacher_slot(
        self, teacher_id: int, weekday: int, lesson_number: int, school_year_id: int
    ) -> Schedule | None:
        stmt = (
            select(Schedule)
            .join(SchoolClass, Schedule.class_id == SchoolClass.id)
            .where(
                Schedule.teacher_id == teacher_id,
                Schedule.weekday == weekday,
                Schedule.lesson_number == lesson_number,
                SchoolClass.school_year_id == school_year_id,
            )
        )
        return self.db.scalars(stmt).first()

    def get_by_teacher(self, teacher_id: int, school_year_id: int) -> list[Schedule]:
        stmt = (
            select(Schedule)
            .join(SchoolClass, Schedule.class_id == SchoolClass.id)
            .where(Schedule.teacher_id == teacher_id, SchoolClass.school_year_id == school_year_id)
            .order_by(Schedule.weekday, Schedule.lesson_number)
        )
        return list(self.db.scalars(stmt).all())

    def update_schedule(self, schedule_id: int, subject_id: int = UNSET, teacher_id: int = UNSET, weekday: int = UNSET, lesson_number: int = UNSET, room: str | None = UNSET) -> Schedule | None:
        slot = self.get_schedule_by_id(schedule_id)
        if slot is None:
            return None
        apply_updates(
            slot,
            subject_id=subject_id,
            teacher_id=teacher_id,
            weekday=weekday,
            lesson_number=lesson_number,
            room=room,
        )
        self.db.commit()
        self.db.refresh(slot)
        return slot