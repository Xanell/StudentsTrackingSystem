from datetime import date
from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class SchoolQuarter(Base):
    __tablename__ = "quarters"
    __table_args__ = (
        UniqueConstraint("school_year_id", "number"),
        CheckConstraint("number BETWEEN 1 AND 4"),
        CheckConstraint("end_date > start_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    school_year_id: Mapped[int] = mapped_column(ForeignKey("school_years.id"))
    number: Mapped[int] = mapped_column(SmallInteger)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)

    school_year: Mapped["SchoolYear"] = relationship(back_populates="quarters")
