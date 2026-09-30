from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..DTOs.Subjects import Subject
from .Common import UNSET, apply_updates

class SubjectsRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_subject(self, name: str, short_name: str | None = None) -> Subject:
        subject = Subject(name=name, short_name=short_name)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def get_by_id(self, subject_id: int) -> Subject | None:
        return self.db.get(Subject, subject_id)

    def get_by_name(self, name: str) -> Subject | None:
        stmt = select(Subject).where(func.lower(Subject.name) == name.strip().lower())
        return self.db.scalars(stmt).first()

    def get_all(self) -> list[Subject]:
        stmt = select(Subject).order_by(Subject.name)
        return list(self.db.scalars(stmt).all())

    def update_subject(self, subject_id: int, name: str = UNSET, short_name: str | None = UNSET) -> Subject | None:
        subject = self.get_by_id(subject_id)
        if subject is None:
            return None
        apply_updates(subject, name=name, short_name=short_name)
        self.db.commit()
        self.db.refresh(subject)
        return subject