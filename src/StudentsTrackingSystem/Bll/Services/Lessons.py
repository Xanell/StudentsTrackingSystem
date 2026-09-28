from datetime import date
from sqlalchemy.orm import Session
from Bll.Schemas.Lessons import LessonDetail, LessonShort, LessonUpdate
from Bll.Services.Calendar import CalendarService
from Core.Exceptions import BusinessValidationError, NotFoundError
from Dal.Repositories.Lessons import LessonsRepository
from Dal.Repositories.Schedule import ScheduleRepository
from Dal.Repositories.SchoolClasses import SchoolClassesRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository

class LessonService:
    """
    Обычные уроки создаются автоматически по расписанию (get_or_create_day),
    когда учитель открывает журнал или ученик — дневник. Создаются только уроки
    на сегодня и прошедшие дни: будущие показываются прямо из расписания, чтобы
    изменения расписания не расходились с уже созданными уроками.
    Вручную (create_lesson) — только замены и перенесённые уроки.
    """

    def __init__(self, session: Session):
        self.lesson_repo = LessonsRepository(session)
        self.schedule_repo = ScheduleRepository(session)
        self.school_class_repo = SchoolClassesRepository(session)
        self.school_year_repo = SchoolYearRepository(session)
        self.calendar_service = CalendarService(session)

    def _get_lesson(self, lesson_id: int):
        lesson = self.lesson_repo.get_by_id(lesson_id)
        if lesson is None:
            raise NotFoundError(f"Урок с id={lesson_id} не найден")
        return lesson

    def _get_class(self, class_id: int):
        school_class = self.school_class_repo.get_class_by_id(class_id)
        if school_class is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")
        return school_class

    def _to_details(self, lessons) -> list[LessonDetail]:
        result = []
        for lesson in lessons:
            result.append(LessonDetail.model_validate(lesson))
        return result

    def _is_class_school_day(self, school_class, day: date) -> bool:
        """Учебный ли день для класса: внутри его учебного года и по календарю."""
        year = school_class.school_year
        if day < year.start_date or day > year.end_date:
            return False
        return self.calendar_service.is_school_day(day)

    def _check_due_date(self, lesson_date: date, homework_due_date: date | None) -> None:
        if homework_due_date is not None and homework_due_date < lesson_date:
            raise BusinessValidationError("Срок сдачи домашки не может быть раньше даты урока")

    def get_or_create_day(self, class_id: int, day: date) -> list[LessonDetail]:
        """Уроки класса на дату. Если день учебный и не в будущем — недостающие уроки создаются по расписанию."""
        school_class = self._get_class(class_id)

        if day <= date.today() and self._is_class_school_day(school_class, day):
            slots = self.schedule_repo.get_by_class_and_weekday(class_id, day.isoweekday())
            for slot in slots:
                existing = self.lesson_repo.get_by_class_date_number(class_id, day, slot.lesson_number)
                if existing is None:
                    self.lesson_repo.create_lesson(
                        class_id=class_id,
                        subject_id=slot.subject_id,
                        teacher_id=slot.teacher_id,
                        lesson_date=day,
                        lesson_number=slot.lesson_number,
                    )

        return self._to_details(self.lesson_repo.get_by_class_and_date(class_id, day))

    def get_teacher_day(self, teacher_id: int, day: date) -> list[LessonDetail]:
        """Уроки учителя на дату — главная страница учителя."""
        year = self.school_year_repo.get_current()
        if year is not None:
            # Сначала создаём уроки во всех классах, где у учителя по расписанию есть урок в этот день.
            class_ids = []
            for slot in self.schedule_repo.get_by_teacher(teacher_id, year.id):
                if slot.weekday == day.isoweekday() and slot.class_id not in class_ids:
                    class_ids.append(slot.class_id)
            for class_id in class_ids:
                self.get_or_create_day(class_id, day)

        return self._to_details(self.lesson_repo.get_by_teacher_and_date(teacher_id, day))

    def update_lesson(self, lesson_id: int, data: LessonUpdate) -> LessonDetail:
        """Тема и домашка. Пустое поле в форме очищает значение."""
        lesson = self._get_lesson(lesson_id)
        self._check_due_date(lesson.lesson_date, data.homework_due_date)
        updated = self.lesson_repo.update_lesson(
            lesson_id,
            topic=data.topic,
            homework=data.homework,
            homework_due_date=data.homework_due_date,
        )
        return LessonDetail.model_validate(updated)

    def get_by_id(self, lesson_id: int) -> LessonDetail:
        return LessonDetail.model_validate(self._get_lesson(lesson_id))

    def get_by_class_and_period(
        self, class_id: int, start_date: date, end_date: date, subject_id: int | None = None
    ) -> list[LessonShort]:
        self._get_class(class_id)
        result = []
        for lesson in self.lesson_repo.get_by_class_and_period(class_id, start_date, end_date, subject_id):
            result.append(LessonShort.model_validate(lesson))
        return result
