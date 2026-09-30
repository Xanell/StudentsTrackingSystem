from datetime import date
from sqlalchemy import CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class SchoolYear(Base):
    __tablename__ = "school_years"
    __table_args__ = (
        CheckConstraint("end_date > start_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)  # 2026/2027
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(default=False)

    quarters: Mapped[list["SchoolQuarter"]] = relationship(
        back_populates="school_year",
        order_by="SchoolQuarter.number",
    )
    days_off: Mapped[list["DayOff"]] = relationship(
        back_populates="school_year",
        order_by="DayOff.start_date",
    )
    school_classes: Mapped[list["SchoolClass"]] = relationship(back_populates="school_year")
