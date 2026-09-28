from datetime import date
from Bll.Schemas.Base import BaseSchema
from Bll.Schemas.Lessons import LessonShort
from Bll.Schemas.SchoolClasses import SchoolClassShort
from Bll.Schemas.Subject import SubjectDetail
from Bll.Schemas.User import UserShort
from Core.Enums import GradeType

class JournalMark(BaseSchema):
    id: int
    grade: int
    grade_type: GradeType

class JournalCell(BaseSchema):
    lesson_id: int
    marks: list[JournalMark] = []
    attendance_id: int | None = None  # None — посещаемость на уроке ещё не отмечали
    is_present: bool | None = None
    absence_reason: str | None = None
 
class JournalRow(BaseSchema):
    student: UserShort
    cells: list[JournalCell]  # в том же порядке, что Journal.lessons
    average: float | None

class Journal(BaseSchema):
    school_class: SchoolClassShort
    subject: SubjectDetail
    start_date: date
    end_date: date
    lessons: list[LessonShort]
    rows: list[JournalRow]

class TeacherJournalLink(BaseSchema):
    school_class: SchoolClassShort
    subject: SubjectDetail
