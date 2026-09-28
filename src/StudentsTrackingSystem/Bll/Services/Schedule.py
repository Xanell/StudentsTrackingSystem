from sqlalchemy.orm import Session
from Bll.Schemas.Schedule import ScheduleCreate, ScheduleDetail, ScheduleUpdate
from Core.Enums import SCHOOL_DAYS_PER_WEEK, WEEKDAY_LABELS, RoleName
from Core.Exceptions import BusinessValidationError, ConflictError, NotFoundError
from Dal.Repositories.Schedule import ScheduleRepository
from Dal.Repositories.SchoolClasses import SchoolClassesRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository
from Dal.Repositories.Subjects import SubjectsRepository
from Dal.Repositories.User import UserRepository

class ScheduleService:
    def __init__(self, session: Session):
        self.schedule_repo = ScheduleRepository(session)
        self.school_class_repo = SchoolClassesRepository(session)
        self.school_year_repo = SchoolYearRepository(session)
        self.subject_repo = SubjectsRepository(session)
        self.user_repo = UserRepository(session)

    def _get_slot(self, schedule_id: int):
        slot = self.schedule_repo.get_schedule_by_id(schedule_id)
        if slot is None:
            raise NotFoundError(f"Урок в расписании с id={schedule_id} не найден")
        return slot

    def _to_details(self, slots) -> list[ScheduleDetail]:
        result = []
        for slot in slots:
            result.append(ScheduleDetail.model_validate(slot))
        return result

    def _check(
        self,
        class_id: int,
        subject_id: int,
        teacher_id: int,
        weekday: int,
        lesson_number: int,
        exclude_id: int | None = None,
    ) -> None:
        school_class = self.school_class_repo.get_class_by_id(class_id)
        if school_class is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")
        if self.subject_repo.get_by_id(subject_id) is None:
            raise NotFoundError(f"Предмет с id={subject_id} не найден")

        teacher = self.user_repo.get_by_id(teacher_id)
        if teacher is None:
            raise NotFoundError(f"Пользователь с id={teacher_id} не найден")
        if teacher.role != RoleName.TEACHER:
            raise BusinessValidationError(f"{teacher.last_name} не учитель")
        if teacher.deactivated_at is not None:
            raise BusinessValidationError(f"Учитель {teacher.last_name} деактивирован")

        if weekday > SCHOOL_DAYS_PER_WEEK:
            raise BusinessValidationError(f"{WEEKDAY_LABELS[weekday]} — не учебный день")

        class_slot = self.schedule_repo.get_by_class_slot(class_id, weekday, lesson_number)
        if class_slot is not None and class_slot.id != exclude_id:
            raise ConflictError(
                f"У класса уже стоит {class_slot.subject.name} — {WEEKDAY_LABELS[weekday]}, {lesson_number} урок"
            )

        teacher_slot = self.schedule_repo.get_teacher_slot(
            teacher_id, weekday, lesson_number, school_class.school_year_id
        )
        if teacher_slot is not None and teacher_slot.id != exclude_id:
            busy_class = teacher_slot.school_class
            raise ConflictError(
                f"Учитель в это время ведёт урок в {busy_class.number}{busy_class.letter} — "
                f"{WEEKDAY_LABELS[weekday]}, {lesson_number} урок"
            )

    def create_schedule(self, data: ScheduleCreate) -> ScheduleDetail:
        self._check(data.class_id, data.subject_id, data.teacher_id, data.weekday, data.lesson_number)
        slot = self.schedule_repo.create_schedule(
            class_id=data.class_id,
            subject_id=data.subject_id,
            teacher_id=data.teacher_id,
            weekday=data.weekday,
            lesson_number=data.lesson_number,
            room=data.room,
        )
        return ScheduleDetail.model_validate(slot)

    def update_schedule(self, schedule_id: int, data: ScheduleUpdate) -> ScheduleDetail:
        slot = self._get_slot(schedule_id)
        self._check(
            slot.class_id, data.subject_id, data.teacher_id, data.weekday, data.lesson_number, exclude_id=schedule_id
        )
        updated = self.schedule_repo.update_schedule(
            schedule_id,
            subject_id=data.subject_id,
            teacher_id=data.teacher_id,
            weekday=data.weekday,
            lesson_number=data.lesson_number,
            room=data.room,
        )
        return ScheduleDetail.model_validate(updated)

    def get_by_id(self, schedule_id: int) -> ScheduleDetail:
        return ScheduleDetail.model_validate(self._get_slot(schedule_id))

    def get_by_class(self, class_id: int) -> list[ScheduleDetail]:
        """Вся неделя класса, отсортирована по дню и номеру урока."""
        if self.school_class_repo.get_class_by_id(class_id) is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")
        return self._to_details(self.schedule_repo.get_by_class(class_id))

    def get_by_teacher(self, teacher_id: int) -> list[ScheduleDetail]:
        """Расписание учителя на текущий учебный год."""
        year = self.school_year_repo.get_current()
        if year is None:
            return []
        return self._to_details(self.schedule_repo.get_by_teacher(teacher_id, year.id))
