from datetime import date, timedelta
from sqlalchemy.orm import Session
from Bll.Schemas.Diary import DiaryDay, DiaryLesson, DiaryMark
from Bll.Services.Calendar import CalendarService
from Bll.Services.Lessons import LessonService
from Core.Enums import LESSON_TIMES, SCHOOL_DAYS_PER_WEEK, DayType, RoleName
from Core.Exceptions import BusinessValidationError, NotFoundError
from Dal.Repositories.Attendance import AttendanceRepository
from Dal.Repositories.Lessons import LessonsRepository
from Dal.Repositories.Mark import MarkRepository
from Dal.Repositories.Schedule import ScheduleRepository
from Dal.Repositories.User import UserRepository

class DiaryService:
    """Дневник ученика на неделю."""

    def __init__(self, session: Session):
        self.user_repo = UserRepository(session)
        self.lesson_repo = LessonsRepository(session)
        self.schedule_repo = ScheduleRepository(session)
        self.mark_repo = MarkRepository(session)
        self.attendance_repo = AttendanceRepository(session)
        self.lesson_service = LessonService(session)
        self.calendar_service = CalendarService(session)

    def get_week(self, student_id: int, any_day: date) -> list[DiaryDay]:
        """Неделя, в которую попадает any_day: с понедельника по последний учебный день недели."""
        student = self.user_repo.get_by_id(student_id)
        if student is None or student.role != RoleName.STUDENT:
            raise NotFoundError(f"Ученик с id={student_id} не найден")
        if student.class_id is None:
            raise BusinessValidationError("Ученик не привязан к классу")

        monday = any_day - timedelta(days=any_day.weekday())
        last_day = monday + timedelta(days=SCHOOL_DAYS_PER_WEEK - 1)
        today = date.today()

        # Уроки на прошедшие дни недели создаются по расписанию, если их ещё нет.
        day = monday
        while day <= last_day and day <= today:
            self.lesson_service.get_or_create_day(student.class_id, day)
            day += timedelta(days=1)

        # Всё нужное за неделю — по одному запросу, дальше только разбор в циклах.
        calendar_days = self.calendar_service.get_period(monday, last_day)
        lessons = self.lesson_repo.get_by_class_and_period(student.class_id, monday, last_day)

        marks_by_lesson = {}
        for mark in self.mark_repo.get_by_student_and_period(student_id, monday, last_day):
            if mark.lesson_id not in marks_by_lesson:
                marks_by_lesson[mark.lesson_id] = []
            marks_by_lesson[mark.lesson_id].append(DiaryMark(grade=mark.grade, grade_type=mark.grade_type))

        absences_by_lesson = {}
        for absence in self.attendance_repo.get_absences_by_student_and_period(student_id, monday, last_day):
            absences_by_lesson[absence.lesson_id] = absence.reason

        result = []
        for calendar_day in calendar_days:
            diary_day = DiaryDay(day=calendar_day.day, day_type=calendar_day.day_type, title=calendar_day.title)
            if calendar_day.day_type == DayType.SCHOOL_DAY:
                if calendar_day.day <= today:
                    diary_day.lessons = self._past_lessons(calendar_day.day, lessons, marks_by_lesson, absences_by_lesson)
                else:
                    diary_day.lessons = self._planned_lessons(student.class_id, calendar_day.day)
            result.append(diary_day)
        return result

    def _past_lessons(self, day: date, lessons, marks_by_lesson: dict, absences_by_lesson: dict) -> list[DiaryLesson]:
        """Проведённые уроки дня с оценками и пропусками."""
        result = []
        for lesson in lessons:
            if lesson.lesson_date != day:
                continue
            start_time, end_time = LESSON_TIMES[lesson.lesson_number]
            diary_lesson = DiaryLesson(
                lesson_id=lesson.id,
                lesson_number=lesson.lesson_number,
                start_time=start_time,
                end_time=end_time,
                subject_name=lesson.subject.name,
                topic=lesson.topic,
                homework=lesson.homework,
                homework_due_date=lesson.homework_due_date,
                marks=marks_by_lesson.get(lesson.id, []),
            )
            if lesson.id in absences_by_lesson:
                diary_lesson.is_absent = True
                diary_lesson.absence_reason = absences_by_lesson[lesson.id]
            result.append(diary_lesson)
        return result

    def _planned_lessons(self, class_id: int, day: date) -> list[DiaryLesson]:
        """Будущие уроки — прямо из расписания."""
        result = []
        for slot in self.schedule_repo.get_by_class_and_weekday(class_id, day.isoweekday()):
            start_time, end_time = LESSON_TIMES[slot.lesson_number]
            result.append(
                DiaryLesson(
                    lesson_id=None,
                    lesson_number=slot.lesson_number,
                    start_time=start_time,
                    end_time=end_time,
                    subject_name=slot.subject.name,
                    room=slot.room,
                )
            )
        return result
