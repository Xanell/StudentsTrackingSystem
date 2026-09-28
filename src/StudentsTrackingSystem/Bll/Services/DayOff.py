from datetime import date
from sqlalchemy.orm import Session
from Bll.Schemas.DayOff import DayOffCreate, DayOffDetail, DayOffUpdate
from Core.Enums import DAY_OFF_TYPES, DayType
from Core.Exceptions import BusinessValidationError, NotFoundError
from Dal.Repositories.DayOff import DayOffRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository

class DayOffService:
    def __init__(self, session: Session):
        self.day_off_repo = DayOffRepository(session)
        self.school_year_repo = SchoolYearRepository(session)

    def _get_day_off(self, day_off_id: int):
        day_off = self.day_off_repo.get_by_id(day_off_id)
        if day_off is None:
            raise NotFoundError(f"Запись календаря с id={day_off_id} не найдена")
        return day_off

    def _check(self, school_year_id: int, start_date: date, end_date: date, day_type: DayType) -> None:
        year = self.school_year_repo.get_by_id(school_year_id)
        if year is None:
            raise NotFoundError(f"Учебный год с id={school_year_id} не найден")
        if end_date < start_date:
            raise BusinessValidationError("Дата окончания не может быть раньше даты начала")
        if start_date < year.start_date or end_date > year.end_date:
            raise BusinessValidationError(f"Даты должны быть внутри учебного года {year.name}")
        if day_type not in DAY_OFF_TYPES:
            raise BusinessValidationError("Выходные вычисляются по дню недели, вручную их вносить не нужно")

    def create_day_off(self, data: DayOffCreate) -> DayOffDetail:
        self._check(data.school_year_id, data.start_date, data.end_date, data.day_type)
        day_off = self.day_off_repo.create_day_off(
            school_year_id=data.school_year_id,
            start_date=data.start_date,
            end_date=data.end_date,
            day_type=data.day_type,
            title=data.title,
        )
        return DayOffDetail.model_validate(day_off)

    def update_day_off(self, day_off_id: int, data: DayOffUpdate) -> DayOffDetail:
        day_off = self._get_day_off(day_off_id)
        self._check(day_off.school_year_id, data.start_date, data.end_date, data.day_type)
        updated = self.day_off_repo.update_day_off(
            day_off_id,
            start_date=data.start_date,
            end_date=data.end_date,
            day_type=data.day_type,
            title=data.title,
        )
        return DayOffDetail.model_validate(updated)

    def get_by_id(self, day_off_id: int) -> DayOffDetail:
        return DayOffDetail.model_validate(self._get_day_off(day_off_id))

    def get_by_year(self, school_year_id: int) -> list[DayOffDetail]:
        if self.school_year_repo.get_by_id(school_year_id) is None:
            raise NotFoundError(f"Учебный год с id={school_year_id} не найден")
        result = []
        for day_off in self.day_off_repo.get_by_year(school_year_id):
            result.append(DayOffDetail.model_validate(day_off))
        return result
