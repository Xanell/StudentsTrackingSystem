from sqlalchemy.orm import Session
from Bll.Schemas.Subject import SubjectCreate, SubjectDetail, SubjectUpdate
from Core.Exceptions import ConflictError, NotFoundError
from Dal.Repositories.Subjects import SubjectsRepository

class SubjectService:
    def __init__(self, session: Session):
        self.subject_repo = SubjectsRepository(session)

    def _get_subject(self, subject_id: int):
        subject = self.subject_repo.get_by_id(subject_id)
        if subject is None:
            raise NotFoundError(f"Предмет с id={subject_id} не найден")
        return subject

    def create_subject(self, data: SubjectCreate) -> SubjectDetail:
        if self.subject_repo.get_by_name(data.name) is not None:
            raise ConflictError(f"Предмет «{data.name}» уже есть")
        subject = self.subject_repo.create_subject(name=data.name, short_name=data.short_name)
        return SubjectDetail.model_validate(subject)

    def update_subject(self, subject_id: int, data: SubjectUpdate) -> SubjectDetail:
        self._get_subject(subject_id)
        existing = self.subject_repo.get_by_name(data.name)
        if existing is not None and existing.id != subject_id:
            raise ConflictError(f"Предмет «{data.name}» уже есть")
        updated = self.subject_repo.update_subject(subject_id, name=data.name, short_name=data.short_name)
        return SubjectDetail.model_validate(updated)

    def get_by_id(self, subject_id: int) -> SubjectDetail:
        return SubjectDetail.model_validate(self._get_subject(subject_id))

    def get_all(self) -> list[SubjectDetail]:
        result = []
        for subject in self.subject_repo.get_all():
            result.append(SubjectDetail.model_validate(subject))
        return result
