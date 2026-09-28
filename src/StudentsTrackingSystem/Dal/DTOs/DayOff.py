from datetime import date
from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Core.Enums import DayType
from .Base import Base, str_enum

class DayOff(Base):
    __tablename__ = "days_off"
    __table_args__ = (
        CheckConstraint("end_date >= start_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    school_year_id: Mapped[int] = mapped_column(ForeignKey("school_years.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    day_type: Mapped[DayType] = mapped_column(str_enum(DayType, "day_type"))
    title: Mapped[str] = mapped_column(String(100))

    school_year: Mapped["SchoolYear"] = relationship(back_populates="days_off")
