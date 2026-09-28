from datetime import date
from sqlalchemy.orm import Session
from Bll.Schemas.SchoolYear import SchoolYearCreate, SchoolYearDetail, SchoolYearUpdate
from Core.Exceptions import BusinessValidationError, ConflictError, NotFoundError
from Dal.Repositories.DayOff import DayOffRepository
from Dal.Repositories.SchoolQuarter import QuarterRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository

class SchoolYearService:
    def __init__(self, session: Session):
        self.school_year_repo = SchoolYearRepository(session)
        self.quarter_repo = QuarterRepository(session)
        self.day_off_repo = DayOffRepository(session)

    def _get_year(self, year_id: int):
        year = self.school_year_repo.get_by_id(year_id)
        if year is None:
            raise NotFoundError(f"Учебный год с id={year_id} не найден")
        return year

    def _check_dates(self, start_date: date, end_date: date, exclude_id: int | None = None) -> str:
        """Проверяет даты и возвращает название года ("2026/2027")."""
        if end_date <= start_date:
            raise BusinessValidationError("Дата окончания должна быть позже даты начала")

        overlapping = self.school_year_repo.get_overlapping(start_date, end_date, exclude_id)
        if len(overlapping) > 0:
            raise ConflictError(f"Даты пересекаются с учебным годом {overlapping[0].name}")

        name = f"{start_date.year}/{end_date.year}"
        existing = self.school_year_repo.get_by_name(name)
        if existing is not None and existing.id != exclude_id:
            raise ConflictError(f"Учебный год {name} уже существует")
        return name

    def create_school_year(self, data: SchoolYearCreate) -> SchoolYearDetail:
        name = self._check_dates(data.start_date, data.end_date)
        year = self.school_year_repo.create_school_year(
            name=name,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return SchoolYearDetail.model_validate(year)

    def update_year(self, year_id: int, data: SchoolYearUpdate) -> SchoolYearDetail:
        self._get_year(year_id)
        name = self._check_dates(data.start_date, data.end_date, exclude_id=year_id)

        # Четверти и нерабочие дни не должны оказаться за границами года.
        for quarter in self.quarter_repo.get_by_year(year_id):
            if quarter.start_date < data.start_date or quarter.end_date > data.end_date:
                raise BusinessValidationError(
                    f"Четверть {quarter.number} выходит за новые границы года. Сначала измените её даты"
                )
        for day_off in self.day_off_repo.get_by_year(year_id):
            if day_off.start_date < data.start_date or day_off.end_date > data.end_date:
                raise BusinessValidationError(
                    f"«{day_off.title}» выходит за новые границы года. Сначала измените его даты"
                )

        updated = self.school_year_repo.update_year(
            year_id,
            name=name,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return SchoolYearDetail.model_validate(updated)

    def get_by_id(self, year_id: int) -> SchoolYearDetail:
        return SchoolYearDetail.model_validate(self._get_year(year_id))

    def get_all(self) -> list[SchoolYearDetail]:
        result = []
        for year in self.school_year_repo.get_all():
            result.append(SchoolYearDetail.model_validate(year))
        return result

    def get_current(self) -> SchoolYearDetail | None:
        year = self.school_year_repo.get_current()
        if year is None:
            return None
        return SchoolYearDetail.model_validate(year)

    def make_current(self, year_id: int) -> SchoolYearDetail:
        self._get_year(year_id)
        return SchoolYearDetail.model_validate(self.school_year_repo.make_current(year_id))
