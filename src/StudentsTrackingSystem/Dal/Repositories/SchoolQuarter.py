from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..DTOs.SchoolQuarter import SchoolQuarter
from .Common import UNSET, apply_updates

class QuarterRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_quarter(self, school_year_id: int, number: int, start_date: date, end_date: date) -> SchoolQuarter:
        quarter = SchoolQuarter(
            school_year_id=school_year_id,
            number=number,
            start_date=start_date,
            end_date=end_date,
        )
        self.db.add(quarter)
        self.db.commit()
        self.db.refresh(quarter)
        return quarter

    def get_by_id(self, quarter_id: int) -> SchoolQuarter | None:
        return self.db.get(SchoolQuarter, quarter_id)

    def get_by_year(self, school_year_id: int) -> list[SchoolQuarter]:
        stmt = (
            select(SchoolQuarter)
            .where(SchoolQuarter.school_year_id == school_year_id)
            .order_by(SchoolQuarter.number)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_number(self, school_year_id: int, number: int) -> SchoolQuarter | None:
        stmt = select(SchoolQuarter).where(
            SchoolQuarter.school_year_id == school_year_id,
            SchoolQuarter.number == number,
        )
        return self.db.scalars(stmt).one_or_none()

    def get_by_date(self, school_year_id: int, day: date) -> SchoolQuarter | None:
        """Четверть, в которую попадает дата. None — это каникулы."""
        stmt = select(SchoolQuarter).where(
            SchoolQuarter.school_year_id == school_year_id,
            SchoolQuarter.start_date <= day,
            SchoolQuarter.end_date >= day,
        )
        return self.db.scalars(stmt).first()

    def get_overlapping(self, school_year_id: int, start_date: date, end_date: date, exclude_id: int | None = None) -> list[SchoolQuarter]:
        """Четверти, пересекающиеся с периодом. Для проверки, что четверти не налезают друг на друга."""
        stmt = select(SchoolQuarter).where(
            SchoolQuarter.school_year_id == school_year_id,
            SchoolQuarter.start_date <= end_date,
            SchoolQuarter.end_date >= start_date,
        )
        if exclude_id is not None:
            stmt = stmt.where(SchoolQuarter.id != exclude_id)
        return list(self.db.scalars(stmt).all())

    def update_quarter(self, quarter_id: int, start_date: date = UNSET, end_date: date = UNSET) -> SchoolQuarter | None:
        quarter = self.get_by_id(quarter_id)
        if quarter is None:
            return None
        apply_updates(quarter, start_date=start_date, end_date=end_date)
        self.db.commit()
        self.db.refresh(quarter)
        return quarter

    # delete_quarter нет: в году всегда 4 четверти, ошибку в датах исправляют через update_quarter.
