from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Bll.Schemas.Subject import SubjectDetail
from Bll.Schemas.User import UserShort
from Core.Enums import MAX_LESSONS_PER_DAY

class ScheduleDetail(BaseSchema):
    id: int
    class_id: int
    weekday: int        # 1 — понедельник
    lesson_number: int  # время звонков — Core.Enums.LESSON_TIMES[lesson_number]
    room: str | None
    subject: SubjectDetail
    teacher: UserShort

class ScheduleCreate(BaseSchema):
    class_id: int
    subject_id: int
    teacher_id: int
    weekday: int = Field(ge=1, le=7)
    lesson_number: int = Field(ge=1, le=MAX_LESSONS_PER_DAY)
    room: str | None = Field(default=None, max_length=10)

class ScheduleUpdate(BaseSchema):
    subject_id: int
    teacher_id: int
    weekday: int = Field(ge=1, le=7)
    lesson_number: int = Field(ge=1, le=MAX_LESSONS_PER_DAY)
    room: str | None = Field(default=None, max_length=10)
