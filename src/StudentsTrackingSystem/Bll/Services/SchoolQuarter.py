from datetime import date
from sqlalchemy.orm import Session
from Bll.Schemas.SchoolQuarter import SchoolQuarterCreate, SchoolQuarterDetail, SchoolQuarterUpdate
from Core.Exceptions import BusinessValidationError, ConflictError, NotFoundError
from Dal.Repositories.SchoolQuarter import QuarterRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository

class SchoolQuarterService:
    def __init__(self, session: Session):
        self.quarter_repo = QuarterRepository(session)
        self.school_year_repo = SchoolYearRepository(session)

    def _get_quarter(self, quarter_id: int):
        quarter = self.quarter_repo.get_by_id(quarter_id)
        if quarter is None:
            raise NotFoundError(f"Четверть с id={quarter_id} не найдена")
        return quarter

    def _check_dates(
        self, school_year_id: int, number: int, start_date: date, end_date: date, exclude_id: int | None = None
    ) -> None:
        year = self.school_year_repo.get_by_id(school_year_id)
        if year is None:
            raise NotFoundError(f"Учебный год с id={school_year_id} не найден")

        if end_date <= start_date:
            raise BusinessValidationError("Дата окончания должна быть позже даты начала")
        if start_date < year.start_date or end_date > year.end_date:
            raise BusinessValidationError(f"Четверть должна быть внутри учебного года {year.name}")

        # Четверти идут по порядку и не пересекаются:
        # предыдущие по номеру заканчиваются раньше, следующие начинаются позже.
        for other in self.quarter_repo.get_by_year(school_year_id):
            if other.id == exclude_id:
                continue
            if other.number < number and other.end_date >= start_date:
                raise BusinessValidationError(
                    f"Четверть {number} должна начинаться после окончания четверти {other.number} ({other.end_date})"
                )
            if other.number > number and other.start_date <= end_date:
                raise BusinessValidationError(
                    f"Четверть {number} должна заканчиваться до начала четверти {other.number} ({other.start_date})"
                )

    def create_quarter(self, data: SchoolQuarterCreate) -> SchoolQuarterDetail:
        if self.quarter_repo.get_by_number(data.school_year_id, data.number) is not None:
            raise ConflictError(f"Четверть {data.number} в этом году уже есть")
        self._check_dates(data.school_year_id, data.number, data.start_date, data.end_date)

        quarter = self.quarter_repo.create_quarter(
            school_year_id=data.school_year_id,
            number=data.number,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return SchoolQuarterDetail.model_validate(quarter)

    def update_quarter(self, quarter_id: int, data: SchoolQuarterUpdate) -> SchoolQuarterDetail:
        quarter = self._get_quarter(quarter_id)
        self._check_dates(quarter.school_year_id, quarter.number, data.start_date, data.end_date, exclude_id=quarter_id)

        updated = self.quarter_repo.update_quarter(
            quarter_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return SchoolQuarterDetail.model_validate(updated)

    def get_by_id(self, quarter_id: int) -> SchoolQuarterDetail:
        return SchoolQuarterDetail.model_validate(self._get_quarter(quarter_id))

    def get_by_year(self, school_year_id: int) -> list[SchoolQuarterDetail]:
        if self.school_year_repo.get_by_id(school_year_id) is None:
            raise NotFoundError(f"Учебный год с id={school_year_id} не найден")
        result = []
        for quarter in self.quarter_repo.get_by_year(school_year_id):
            result.append(SchoolQuarterDetail.model_validate(quarter))
        return result

    def get_current(self) -> SchoolQuarterDetail | None:
        """Текущая четверть текущего года. None — сейчас каникулы или текущий год не выбран."""
        year = self.school_year_repo.get_current()
        if year is None:
            return None
        quarter = self.quarter_repo.get_by_date(year.id, date.today())
        if quarter is None:
            return None
        return SchoolQuarterDetail.model_validate(quarter)
