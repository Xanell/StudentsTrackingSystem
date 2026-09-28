from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..DTOs.HomeworkSubmission import HomeworkSubmission
from ..DTOs.Lessons import Lesson

class HomeworkSubmissionRepository:

    def __init__(self, session: Session):
        self.db = session

    def create_submission(self, lesson_id: int, student_id: int, file_path: str, original_name: str, comment: str | None = None) -> HomeworkSubmission:
        submission = HomeworkSubmission(
            lesson_id=lesson_id,
            student_id=student_id,
            file_path=file_path,
            original_name=original_name,
            comment=comment,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_by_id(self, submission_id: int) -> HomeworkSubmission | None:
        return self.db.get(HomeworkSubmission, submission_id)

    def get_latest(self, lesson_id: int, student_id: int) -> HomeworkSubmission | None:
        stmt = (
            select(HomeworkSubmission)
            .where(HomeworkSubmission.lesson_id == lesson_id, HomeworkSubmission.student_id == student_id)
            .order_by(HomeworkSubmission.submitted_at.desc(), HomeworkSubmission.id.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def get_by_lesson(self, lesson_id: int) -> list[HomeworkSubmission]:
        stmt = (
            select(HomeworkSubmission)
            .where(HomeworkSubmission.lesson_id == lesson_id)
            .order_by(HomeworkSubmission.submitted_at, HomeworkSubmission.id)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_student_and_period(self, student_id: int, start_date: date, end_date: date) -> list[HomeworkSubmission]:
        stmt = (
            select(HomeworkSubmission)
            .join(Lesson, HomeworkSubmission.lesson_id == Lesson.id)
            .where(
                HomeworkSubmission.student_id == student_id,
                Lesson.lesson_date >= start_date,
                Lesson.lesson_date <= end_date,
            )
            .options(joinedload(HomeworkSubmission.lesson))
            .order_by(Lesson.lesson_date, HomeworkSubmission.submitted_at)
        )
        return list(self.db.scalars(stmt).all())
