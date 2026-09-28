from pydantic import Field
from Bll.Schemas.Base import BaseSchema

class AttendanceDetail(BaseSchema):
    id: int
    lesson_id: int
    student_id: int
    is_present: bool

class AttendanceItem(BaseSchema):
    student_id: int
    is_present: bool = True

class AttendanceSave(BaseSchema):
    lesson_id: int
    items: list[AttendanceItem]

class AttendanceUpdate(BaseSchema):
    is_present: bool
