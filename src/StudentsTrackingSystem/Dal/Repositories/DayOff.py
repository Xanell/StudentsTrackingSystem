from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from Core.Enums import DayType
from ..DTOs.DayOff import DayOff
from .Common import UNSET, apply_updates

class DayOffRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_day_off(self, school_year_id: int, start_date: date, end_date: date, day_type: DayType, title: str) -> DayOff:
        day_off = DayOff(
            school_year_id=school_year_id,
            start_date=start_date,
            end_date=end_date,
            day_type=day_type,
            title=title,
        )
        self.db.add(day_off)
        self.db.commit()
        self.db.refresh(day_off)
        return day_off

    def get_by_id(self, day_off_id: int) -> DayOff | None:
        return self.db.get(DayOff, day_off_id)

    def get_by_year(self, school_year_id: int) -> list[DayOff]:
        stmt = (
            select(DayOff)
            .where(DayOff.school_year_id == school_year_id)
            .order_by(DayOff.start_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_in_range(self, start_date: date, end_date: date) -> list[DayOff]:
        stmt = (
            select(DayOff)
            .where(DayOff.start_date <= end_date, DayOff.end_date >= start_date)
            .order_by(DayOff.start_date)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_date(self, day: date) -> DayOff | None:
        stmt = select(DayOff).where(DayOff.start_date <= day, DayOff.end_date >= day)
        return self.db.scalars(stmt).first()

    def update_day_off(self, day_off_id: int, start_date: date = UNSET, end_date: date = UNSET, day_type: DayType = UNSET, title: str = UNSET) -> DayOff | None:
        day_off = self.get_by_id(day_off_id)
        if day_off is None:
            return None
        apply_updates(day_off, start_date=start_date, end_date=end_date, day_type=day_type, title=title)
        self.db.commit()
        self.db.refresh(day_off)
        return day_off
