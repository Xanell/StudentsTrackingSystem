from datetime import date
from sqlalchemy.orm import Session
from Bll.Schemas.Journal import Journal, JournalCell, JournalMark, JournalRow, TeacherJournalLink
from Bll.Schemas.Lessons import LessonShort
from Bll.Schemas.SchoolClasses import SchoolClassShort
from Bll.Schemas.Subject import SubjectDetail
from Bll.Schemas.User import UserShort
from Bll.Services.Mark import calculate_average
from Core.Exceptions import NotFoundError
from Dal.Repositories.Attendance import AttendanceRepository
from Dal.Repositories.Lessons import LessonsRepository
from Dal.Repositories.Mark import MarkRepository
from Dal.Repositories.Schedule import ScheduleRepository
from Dal.Repositories.SchoolClasses import SchoolClassesRepository
from Dal.Repositories.SchoolQuarter import QuarterRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository
from Dal.Repositories.Subjects import SubjectsRepository
from Dal.Repositories.User import UserRepository

class JournalService:
    """Журнал учителя: таблица «ученики × уроки» по одному предмету в одном классе."""

    def __init__(self, session: Session):
        self.school_class_repo = SchoolClassesRepository(session)
        self.subject_repo = SubjectsRepository(session)
        self.quarter_repo = QuarterRepository(session)
        self.school_year_repo = SchoolYearRepository(session)
        self.schedule_repo = ScheduleRepository(session)
        self.lesson_repo = LessonsRepository(session)
        self.user_repo = UserRepository(session)
        self.mark_repo = MarkRepository(session)
        self.attendance_repo = AttendanceRepository(session)

    def get_journal(self, class_id: int, subject_id: int, start_date: date, end_date: date) -> Journal:
        school_class = self.school_class_repo.get_class_by_id(class_id)
        if school_class is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")
        subject = self.subject_repo.get_by_id(subject_id)
        if subject is None:
            raise NotFoundError(f"Предмет с id={subject_id} не найден")

        lessons = self.lesson_repo.get_by_class_and_period(class_id, start_date, end_date, subject_id)
        lesson_ids = []
        for lesson in lessons:
            lesson_ids.append(lesson.id)

        # Выбывшие ученики тоже показываются: их оценки за период должны быть видны.
        students = self.user_repo.get_students_by_class(class_id, include_inactive=True)

        # Все оценки и отметки за период — двумя запросами, дальше раскладываем по клеткам.
        marks_by_cell = {}
        for mark in self.mark_repo.get_by_lesson_ids(lesson_ids):
            key = (mark.student_id, mark.lesson_id)
            if key not in marks_by_cell:
                marks_by_cell[key] = []
            marks_by_cell[key].append(mark)

        attendance_by_cell = {}
        for record in self.attendance_repo.get_by_lesson_ids(lesson_ids):
            attendance_by_cell[(record.student_id, record.lesson_id)] = record

        rows = []
        for student in students:
            cells = []
            grades = []
            for lesson in lessons:
                cell = JournalCell(lesson_id=lesson.id)
                for mark in marks_by_cell.get((student.id, lesson.id), []):
                    cell.marks.append(JournalMark(id=mark.id, grade=mark.grade, grade_type=mark.grade_type))
                    grades.append(mark.grade)
                record = attendance_by_cell.get((student.id, lesson.id))
                if record is not None:
                    cell.attendance_id = record.id
                    cell.is_present = record.is_present
                    cell.absence_reason = record.reason
                cells.append(cell)
            rows.append(
                JournalRow(
                    student=UserShort.model_validate(student),
                    cells=cells,
                    average=calculate_average(grades),
                )
            )

        lesson_shorts = []
        for lesson in lessons:
            lesson_shorts.append(LessonShort.model_validate(lesson))

        return Journal(
            school_class=SchoolClassShort.model_validate(school_class),
            subject=SubjectDetail.model_validate(subject),
            start_date=start_date,
            end_date=end_date,
            lessons=lesson_shorts,
            rows=rows,
        )

    def get_journal_for_quarter(self, class_id: int, subject_id: int, quarter_id: int) -> Journal:
        quarter = self.quarter_repo.get_by_id(quarter_id)
        if quarter is None:
            raise NotFoundError(f"Четверть с id={quarter_id} не найдена")
        return self.get_journal(class_id, subject_id, quarter.start_date, quarter.end_date)

    def get_teacher_journals(self, teacher_id: int) -> list[TeacherJournalLink]:
        """Какие журналы (класс + предмет) учитель ведёт в текущем году — по расписанию."""
        year = self.school_year_repo.get_current()
        if year is None:
            return []

        seen = []
        result = []
        for slot in self.schedule_repo.get_by_teacher(teacher_id, year.id):
            key = (slot.class_id, slot.subject_id)
            if key in seen:
                continue
            seen.append(key)
            result.append(
                TeacherJournalLink(
                    school_class=SchoolClassShort.model_validate(slot.school_class),
                    subject=SubjectDetail.model_validate(slot.subject),
                )
            )
        return result
