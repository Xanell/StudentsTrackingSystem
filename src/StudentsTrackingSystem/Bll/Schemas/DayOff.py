from datetime import date
from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Core.Enums import DayType

class DayOffDetail(BaseSchema):
    id: int
    school_year_id: int
    start_date: date
    end_date: date
    day_type: DayType
    title: str

class DayOffCreate(BaseSchema):
    school_year_id: int
    start_date: date
    end_date: date   # для одного дня равен start_date
    day_type: DayType
    title: str = Field(min_length=1, max_length=100)

class DayOffUpdate(BaseSchema):
    start_date: date
    end_date: date
    day_type: DayType  # ошибочный праздник переключают в DayType.SCHOOL_DAY
    title: str = Field(min_length=1, max_length=100)

class CalendarDay(BaseSchema):
    day: date
    day_type: DayType
    title: str | None = None  # название праздника или «Осенние каникулы»
