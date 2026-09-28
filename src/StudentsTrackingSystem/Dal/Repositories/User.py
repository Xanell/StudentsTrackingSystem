from sqlalchemy import func, select
from sqlalchemy.orm import Session
from Core.Enums import RoleName
from ..DTOs.User import User
from .Common import UNSET, apply_updates

class UserRepository:
    def __init__(self, session: Session):
        self.db = session

    def create_user(self, username: str, password_hash: str, last_name: str, first_name: str, middle_name: str, role: RoleName, class_id: int | None = None) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            role=role,
            class_id=class_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.scalars(stmt).one_or_none()

    def _list(self, *conditions, include_inactive: bool = False) -> list[User]:
        stmt = select(User).where(*conditions)
        if not include_inactive:
            stmt = stmt.where(User.deactivated_at.is_(None))
        stmt = stmt.order_by(User.last_name, User.first_name)
        return list(self.db.scalars(stmt).all())

    def get_all(self, include_inactive: bool = False) -> list[User]:
        return self._list(include_inactive=include_inactive)

    def get_by_role(self, role: RoleName, include_inactive: bool = False) -> list[User]:
        return self._list(User.role == role, include_inactive=include_inactive)

    def get_students_by_class(self, class_id: int, include_inactive: bool = False) -> list[User]:
        return self._list(
            User.class_id == class_id,
            User.role == RoleName.STUDENT,
            include_inactive=include_inactive,
        )

    def get_students_without_class(self) -> list[User]:
        return self._list(User.class_id.is_(None), User.role == RoleName.STUDENT)

    def get_inactive(self) -> list[User]:
        stmt = (
            select(User)
            .where(User.deactivated_at.is_not(None))
            .order_by(User.deactivated_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def update_user(self, user_id: int, username: str = UNSET, last_name: str = UNSET, first_name: str = UNSET, middle_name: str = UNSET, role: RoleName = UNSET, class_id: int | None = UNSET) -> User | None:
        user = self.get_by_id(user_id)
        if user is None:
            return None
        apply_updates(user, username=username, last_name=last_name, first_name=first_name, middle_name=middle_name, role=role, class_id=class_id)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_password(self, user_id: int, password_hash: str) -> User | None:
        user = self.get_by_id(user_id)
        if user is None:
            return None
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def move_students(self, from_class_id: int, to_class_id: int) -> int:
        students = self.get_students_by_class(from_class_id)
        for student in students:
            student.class_id = to_class_id
        self.db.commit()
        return len(students)

    def deactivate_user(self, user_id: int) -> User | None:
        user = self.get_by_id(user_id)
        if user is None:
            return None
        if user.deactivated_at is None:
            user.deactivated_at = func.now()
            self.db.commit()
            self.db.refresh(user)
        return user

    def restore_user(self, user_id: int) -> User | None:
        user = self.get_by_id(user_id)
        if user is None:
            return None
        user.deactivated_at = None
        self.db.commit()
        self.db.refresh(user)
        return user
