from datetime import date
from pydantic import Field
from Bll.Schemas.Base import BaseSchema

class SchoolQuarterDetail(BaseSchema):
    id: int
    school_year_id: int
    number: int
    start_date: date
    end_date: date

class SchoolQuarterCreate(BaseSchema):
    school_year_id: int
    number: int = Field(ge=1, le=4)
    start_date: date
    end_date: date

class SchoolQuarterUpdate(BaseSchema):
    start_date: date
    end_date: date
