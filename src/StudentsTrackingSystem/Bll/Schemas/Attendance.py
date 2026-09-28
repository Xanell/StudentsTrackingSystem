from pydantic import Field
from Bll.Schemas.Base import BaseSchema

class AttendanceDetail(BaseSchema):
    id: int
    lesson_id: int
    student_id: int
    is_present: bool
    reason: str | None

class AttendanceItem(BaseSchema):
    student_id: int
    is_present: bool = True
    reason: str | None = Field(default=None, max_length=255)  # у присутствующих сбрасывается в None

class AttendanceSave(BaseSchema):
    lesson_id: int
    items: list[AttendanceItem]

class AttendanceUpdate(BaseSchema):
    is_present: bool
    reason: str | None = Field(default=None, max_length=255)
