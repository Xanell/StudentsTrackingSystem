from datetime import date
from Bll.Schemas.Base import BaseSchema

class SchoolYearDetail(BaseSchema):
    id: int
    name: str  # "2026/2027"
    start_date: date
    end_date: date
    is_current: bool

class SchoolYearCreate(BaseSchema):
    start_date: date
    end_date: date

class SchoolYearUpdate(BaseSchema):
    start_date: date
    end_date: date
