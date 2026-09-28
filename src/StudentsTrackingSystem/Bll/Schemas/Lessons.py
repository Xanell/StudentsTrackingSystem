from datetime import date
from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Bll.Schemas.SchoolClasses import SchoolClassShort
from Bll.Schemas.Subject import SubjectDetail
from Bll.Schemas.User import UserShort

class LessonShort(BaseSchema):
    """Строка в списке уроков / столбец в журнале."""

    id: int
    lesson_date: date
    lesson_number: int
    topic: str | None
    subject: SubjectDetail

class LessonDetail(BaseSchema):
    id: int
    lesson_date: date
    lesson_number: int
    topic: str | None
    homework: str | None
    homework_due_date: date | None  # None — к следующему уроку
    school_class: SchoolClassShort
    subject: SubjectDetail
    teacher: UserShort

class LessonUpdate(BaseSchema):
    topic: str | None = Field(default=None, max_length=255)
    homework: str | None = None
    homework_due_date: date | None = None
