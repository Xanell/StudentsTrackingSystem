from datetime import date
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from ..DTOs.SchoolYear import SchoolYear
from .Common import UNSET, apply_updates

class SchoolYearRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_school_year(self, name: str, start_date: date, end_date: date, is_current: bool = False) -> SchoolYear:
        year = SchoolYear(name=name, start_date=start_date, end_date=end_date, is_current=is_current)
        self.db.add(year)
        self.db.commit()
        self.db.refresh(year)
        return year

    def get_by_id(self, year_id: int) -> SchoolYear | None:
        return self.db.get(SchoolYear, year_id)

    def get_by_name(self, name: str) -> SchoolYear | None:
        stmt = select(SchoolYear).where(SchoolYear.name == name)
        return self.db.scalars(stmt).one_or_none()

    def get_all(self) -> list[SchoolYear]:
        stmt = select(SchoolYear).order_by(SchoolYear.start_date.desc())
        return list(self.db.scalars(stmt).all())

    def get_current(self) -> SchoolYear | None:
        stmt = select(SchoolYear).where(SchoolYear.is_current.is_(True))
        return self.db.scalars(stmt).one_or_none()

    def get_by_date(self, day: date) -> SchoolYear | None:
        """Учебный год, в который попадает дата."""
        stmt = select(SchoolYear).where(SchoolYear.start_date <= day, SchoolYear.end_date >= day)
        return self.db.scalars(stmt).first()

    def get_overlapping(self, start_date: date, end_date: date, exclude_id: int | None = None) -> list[SchoolYear]:
        """Годы, пересекающиеся с периодом. Для проверки при создании/изменении года."""
        stmt = select(SchoolYear).where(SchoolYear.start_date <= end_date, SchoolYear.end_date >= start_date)
        if exclude_id is not None:
            stmt = stmt.where(SchoolYear.id != exclude_id)
        return list(self.db.scalars(stmt).all())

    def get_past_years(self) -> list[SchoolYear]:
        stmt = (
            select(SchoolYear)
            .where(SchoolYear.end_date < date.today())
            .order_by(SchoolYear.end_date.desc())
        )
        return list(self.db.scalars(stmt).all())

    def make_current(self, year_id: int) -> SchoolYear | None:
        """Снимает флаг со всех годов и ставит на указанный — одной транзакцией."""
        year = self.get_by_id(year_id)
        if year is None:
            return None
        self.db.execute(update(SchoolYear).where(SchoolYear.is_current.is_(True)).values(is_current=False))
        self.db.flush()
        year.is_current = True
        self.db.commit()
        self.db.refresh(year)
        return year

    def update_year(self, year_id: int, name: str = UNSET, start_date: date = UNSET, end_date: date = UNSET) -> SchoolYear | None:
        year = self.get_by_id(year_id)
        if year is None:
            return None
        apply_updates(year, name=name, start_date=start_date, end_date=end_date)
        self.db.commit()
        self.db.refresh(year)
        return year

    # delete_year нет: учебные годы не удаляются, только редактируются.
