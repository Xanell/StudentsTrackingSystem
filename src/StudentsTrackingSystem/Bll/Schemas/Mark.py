from datetime import datetime
from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Core.Enums import GradeType

class MarkDetail(BaseSchema):
    id: int
    lesson_id: int
    student_id: int
    grade: int | None  # None — клетка очищена
    grade_type: GradeType
    created_at: datetime

class MarkSet(BaseSchema):
    lesson_id: int
    student_id: int
    grade_type: GradeType
    grade: int = Field(ge=1, le=5)
