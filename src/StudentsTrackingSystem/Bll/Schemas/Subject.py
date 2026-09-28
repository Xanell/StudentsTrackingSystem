from pydantic import Field
from Bll.Schemas.Base import BaseSchema

class SubjectDetail(BaseSchema):
    id: int
    name: str
    short_name: str | None
class SubjectCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=50)
    short_name: str | None = Field(default=None, max_length=10)

class SubjectUpdate(BaseSchema):
    name: str = Field(min_length=1, max_length=50)
    short_name: str | None = Field(default=None, max_length=10)
