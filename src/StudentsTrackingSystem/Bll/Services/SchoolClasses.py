from sqlalchemy.orm import Session
from Bll.Schemas.SchoolClasses import SchoolClassCreate, SchoolClassDetail, SchoolClassShort, SchoolClassUpdate
from Core.Exceptions import BusinessValidationError, ConflictError, NotFoundError
from Dal.Repositories.SchoolClasses import SchoolClassesRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository
from Dal.Repositories.User import UserRepository

class SchoolClassService:
    def __init__(self, session: Session):
        self.school_class_repo = SchoolClassesRepository(session)
        self.school_year_repo = SchoolYearRepository(session)
        self.user_repo = UserRepository(session)

    def _get_class(self, class_id: int):
        school_class = self.school_class_repo.get_class_by_id(class_id)
        if school_class is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")
        return school_class

    def _to_shorts(self, classes) -> list[SchoolClassShort]:
        result = []
        for school_class in classes:
            result.append(SchoolClassShort.model_validate(school_class))
        return result

    def create_class(self, data: SchoolClassCreate) -> SchoolClassDetail:
        if self.school_year_repo.get_by_id(data.school_year_id) is None:
            raise NotFoundError(f"Учебный год с id={data.school_year_id} не найден")
        if self.school_class_repo.get_by_number_letter_year(data.number, data.letter, data.school_year_id) is not None:
            raise ConflictError(f"Класс {data.number}{data.letter.upper()} в этом году уже есть")

        school_class = self.school_class_repo.create_class(
            number=data.number,
            letter=data.letter,
            school_year_id=data.school_year_id,
        )
        return SchoolClassDetail.model_validate(school_class)

    def update_class(self, class_id: int, data: SchoolClassUpdate) -> SchoolClassDetail:
        school_class = self._get_class(class_id)
        existing = self.school_class_repo.get_by_number_letter_year(data.number, data.letter, school_class.school_year_id)
        if existing is not None and existing.id != class_id:
            raise ConflictError(f"Класс {data.number}{data.letter.upper()} в этом году уже есть")

        updated = self.school_class_repo.update_class(class_id, number=data.number, letter=data.letter)
        return SchoolClassDetail.model_validate(updated)

    def get_by_id(self, class_id: int) -> SchoolClassDetail:
        return SchoolClassDetail.model_validate(self._get_class(class_id))

    def get_by_year(self, school_year_id: int) -> list[SchoolClassShort]:
        if self.school_year_repo.get_by_id(school_year_id) is None:
            raise NotFoundError(f"Учебный год с id={school_year_id} не найден")
        return self._to_shorts(self.school_class_repo.get_classes_by_year(school_year_id))

    def get_current_year_classes(self) -> list[SchoolClassShort]:
        """Классы текущего учебного года. Пустой список, если текущий год не выбран."""
        year = self.school_year_repo.get_current()
        if year is None:
            return []
        return self._to_shorts(self.school_class_repo.get_classes_by_year(year.id))

    def transfer_students(self, from_class_id: int, to_class_id: int) -> int:
        """
        Перевод класса в следующий учебный год (5А 2025/26 -> 6А 2026/27).
        Возвращает, сколько учеников переведено.
        """
        from_class = self._get_class(from_class_id)
        to_class = self._get_class(to_class_id)
        if to_class.school_year.start_date <= from_class.school_year.start_date:
            raise BusinessValidationError("Переводить учеников можно только в класс следующего учебного года")
        return self.user_repo.move_students(from_class_id, to_class_id)
