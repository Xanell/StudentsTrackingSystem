from datetime import datetime
from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Bll.Schemas.User import UserShort

class HomeworkSubmissionDetail(BaseSchema):
    id: int
    lesson_id: int
    student: UserShort
    original_name: str
    comment: str | None
    submitted_at: datetime

class HomeworkSubmissionCreate(BaseSchema):
    lesson_id: int
    comment: str | None = Field(default=None, max_length=500)
