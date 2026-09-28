from datetime import datetime
from Bll.Schemas.Base import BaseSchema

class LessonFileDetail(BaseSchema):
    id: int
    lesson_id: int
    original_name: str
    uploaded_at: datetime
