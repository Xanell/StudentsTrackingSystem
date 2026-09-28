from datetime import date, time
from Bll.Schemas.Base import BaseSchema
from Core.Enums import DayType, GradeType

class DiaryMark(BaseSchema):
    grade: int
    grade_type: GradeType

class DiaryLesson(BaseSchema):
    lesson_id: int | None
    lesson_number: int
    start_time: time
    end_time: time
    subject_name: str
    room: str | None = None
    topic: str | None = None
    homework: str | None = None
    homework_due_date: date | None = None
    marks: list[DiaryMark] = []
    is_absent: bool = False
    absence_reason: str | None = None

class DiaryDay(BaseSchema):
    day: date
    day_type: DayType
    title: str | None = None  # праздник или название каникул
    lessons: list[DiaryLesson] = []
