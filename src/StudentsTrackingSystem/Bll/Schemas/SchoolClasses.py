from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Bll.Schemas.SchoolYear import SchoolYearDetail

class SchoolClassShort(BaseSchema):
    id: int
    number: int
    letter: str
    school_year_id: int

class SchoolClassDetail(BaseSchema):
    id: int
    number: int
    letter: str
    school_year: SchoolYearDetail

class SchoolClassCreate(BaseSchema):
    number: int = Field(ge=1, le=11)
    letter: str = Field(min_length=1, max_length=1)  # в верхний регистр переводит репозиторий
    school_year_id: int

class SchoolClassUpdate(BaseSchema):
    number: int = Field(ge=1, le=11)
    letter: str = Field(min_length=1, max_length=1)
