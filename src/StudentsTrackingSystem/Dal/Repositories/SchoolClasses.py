from sqlalchemy import select
from sqlalchemy.orm import Session
from ..DTOs.SchoolClasses import SchoolClass
from .Common import UNSET, apply_updates

class SchoolClassesRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_class(self, number: int, letter: str, school_year_id: int) -> SchoolClass:
        school_class = SchoolClass(number=number, letter=letter.upper(), school_year_id=school_year_id)
        self.db.add(school_class)
        self.db.commit()
        self.db.refresh(school_class)
        return school_class

    def get_class_by_id(self, class_id: int) -> SchoolClass | None:
        return self.db.get(SchoolClass, class_id)

    def get_by_number_letter_year(self, number: int, letter: str, school_year_id: int) -> SchoolClass | None:
        stmt = select(SchoolClass).where(
            SchoolClass.number == number,
            SchoolClass.letter == letter.upper(),
            SchoolClass.school_year_id == school_year_id,
        )
        return self.db.scalars(stmt).one_or_none()

    def get_all_classes(self) -> list[SchoolClass]:
        stmt = select(SchoolClass).order_by(SchoolClass.number, SchoolClass.letter)
        return list(self.db.scalars(stmt).all())

    def get_classes_by_year(self, school_year_id: int) -> list[SchoolClass]:
        stmt = (
            select(SchoolClass)
            .where(SchoolClass.school_year_id == school_year_id)
            .order_by(SchoolClass.number, SchoolClass.letter)
        )
        return list(self.db.scalars(stmt).all())

    def update_class(self, class_id: int, number: int = UNSET, letter: str = UNSET) -> SchoolClass | None:
        school_class = self.get_class_by_id(class_id)
        if school_class is None:
            return None
        apply_updates(school_class, number=number, letter=letter.upper() if letter else letter)
        self.db.commit()
        self.db.refresh(school_class)
        return school_class

    # delete_class нет: классы не удаляются, только редактируются.
