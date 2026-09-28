import calendar
from datetime import date, timedelta
from sqlalchemy.orm import Session
from Bll.Schemas.DayOff import CalendarDay
from Core.Enums import SCHOOL_DAYS_PER_WEEK, DayType
from Dal.Repositories.DayOff import DayOffRepository
from Dal.Repositories.SchoolQuarter import QuarterRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository

# Каникулы после четверти с этим номером.
VACATION_TITLES = {
    1: "Осенние каникулы",
    2: "Зимние каникулы",
    3: "Весенние каникулы",
}
SUMMER_VACATION = "Летние каникулы"

class CalendarService:
    """
    Тип дня определяется так (первое подходящее правило):
    1. есть запись в days_off — берём её тип и название;
    2. день недели за пределами учебной недели — выходной;
    3. день вне учебного года или до первой четверти — летние каникулы;
    4. день внутри четверти — учебный;
    5. иначе — каникулы после предыдущей четверти.
    """

    def __init__(self, session: Session):
        self.school_year_repo = SchoolYearRepository(session)
        self.quarter_repo = QuarterRepository(session)
        self.day_off_repo = DayOffRepository(session)

    def _load(self, start_date: date, end_date: date):
        """Загружает всё нужное для периода: годы, их четверти и нерабочие дни — без запросов в цикле по дням."""
        years = self.school_year_repo.get_overlapping(start_date, end_date)
        quarters_by_year = {}
        for year in years:
            quarters_by_year[year.id] = self.quarter_repo.get_by_year(year.id)
        days_off = self.day_off_repo.get_in_range(start_date, end_date)
        return years, quarters_by_year, days_off

    def _resolve(self, day: date, years, quarters_by_year, days_off) -> CalendarDay:
        for day_off in days_off:
            if day_off.start_date <= day <= day_off.end_date:
                return CalendarDay(day=day, day_type=day_off.day_type, title=day_off.title)

        if day.isoweekday() > SCHOOL_DAYS_PER_WEEK:
            return CalendarDay(day=day, day_type=DayType.WEEKEND)

        current_year = None
        for year in years:
            if year.start_date <= day <= year.end_date:
                current_year = year
                break
        if current_year is None:
            return CalendarDay(day=day, day_type=DayType.VACATION, title=SUMMER_VACATION)

        previous_quarter = None
        for quarter in quarters_by_year[current_year.id]:
            if quarter.start_date <= day <= quarter.end_date:
                return CalendarDay(day=day, day_type=DayType.SCHOOL_DAY)
            if quarter.end_date < day:
                previous_quarter = quarter

        if previous_quarter is None:
            return CalendarDay(day=day, day_type=DayType.VACATION, title=SUMMER_VACATION)
        title = VACATION_TITLES.get(previous_quarter.number, SUMMER_VACATION)
        return CalendarDay(day=day, day_type=DayType.VACATION, title=title)

    def get_period(self, start_date: date, end_date: date) -> list[CalendarDay]:
        years, quarters_by_year, days_off = self._load(start_date, end_date)
        result = []
        day = start_date
        while day <= end_date:
            result.append(self._resolve(day, years, quarters_by_year, days_off))
            day += timedelta(days=1)
        return result

    def get_month(self, year: int, month: int) -> list[CalendarDay]:
        """Все дни месяца — для страницы календаря."""
        days_in_month = calendar.monthrange(year, month)[1]
        return self.get_period(date(year, month, 1), date(year, month, days_in_month))

    def get_day(self, day: date) -> CalendarDay:
        return self.get_period(day, day)[0]

    def is_school_day(self, day: date) -> bool:
        return self.get_day(day).day_type == DayType.SCHOOL_DAY
