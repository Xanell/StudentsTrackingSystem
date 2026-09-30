import secrets
import string
from sqlalchemy.orm import Session
from Bll.Schemas.User import UserCreate, UserCredentials, UserDetail, UserLogin, UserShort, UserUpdate
from Core.Enums import RoleName
from Core.Exceptions import BusinessValidationError, NotFoundError
from Core.Security import hash_password, verify_password
from Dal.Repositories.Schedule import ScheduleRepository
from Dal.Repositories.SchoolClasses import SchoolClassesRepository
from Dal.Repositories.SchoolYear import SchoolYearRepository
from Dal.Repositories.User import UserRepository
PASSWORD_LENGTH = 8
PASSWORD_ALPHABET = string.ascii_letters + string.digits

class UserService:
    def __init__(self, session: Session):
        self.user_repo = UserRepository(session)
        self.school_class_repo = SchoolClassesRepository(session)
        self.school_year_repo = SchoolYearRepository(session)
        self.schedule_repo = ScheduleRepository(session)

    def _get_user(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"Пользователь с id={user_id} не найден")
        return user

    def _generate_username(self, last_name: str, first_name: str, middle_name: str) -> str:
        base = f"{last_name}{first_name[0].upper()}{middle_name[0].upper()}"
        username = base
        counter = 2
        while self.user_repo.get_by_username(username) is not None:
            username = f"{base}{counter}"
            counter += 1
        return username

    def _generate_password(self) -> str:
        password = ""
        for _ in range(PASSWORD_LENGTH):
            password += secrets.choice(PASSWORD_ALPHABET)
        return password

    def _check_class(self, role: RoleName, class_id: int | None) -> None:
        if class_id is None:
            return
        if role != RoleName.STUDENT:
            raise BusinessValidationError("Только ученик может быть привязан к классу")
        if self.school_class_repo.get_class_by_id(class_id) is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")

    def _has_current_schedule(self, teacher_id: int) -> bool:
        year = self.school_year_repo.get_current()
        if year is None:
            return False
        slots = self.schedule_repo.get_by_teacher(teacher_id, year.id)
        return len(slots) > 0

    def _to_details(self, users) -> list[UserDetail]:
        result = []
        for user in users:
            result.append(UserDetail.model_validate(user))
        return result

    def _to_shorts(self, users) -> list[UserShort]:
        result = []
        for user in users:
            result.append(UserShort.model_validate(user))
        return result

    def create_user(self, data: UserCreate) -> UserCredentials:

        username = self._generate_username(data.last_name, data.first_name, data.middle_name)
        password = self._generate_password()

        user = self.user_repo.create_user(
            username=username,
            password_hash=hash_password(password),
            last_name=data.last_name,
            first_name=data.first_name,
            middle_name=data.middle_name,
            role=data.role,
        )
        return UserCredentials(id=user.id, username=user.username, password=password)

    def get_by_id(self, user_id: int) -> UserDetail:
        return UserDetail.model_validate(self._get_user(user_id))

    def get_all(self) -> list[UserDetail]:
        return self._to_details(self.user_repo.get_all())

    def get_inactive(self) -> list[UserDetail]:
        return self._to_details(self.user_repo.get_inactive())

    def get_by_role(self, role: RoleName) -> list[UserShort]:
        return self._to_shorts(self.user_repo.get_by_role(role))

    def get_teachers(self) -> list[UserShort]:
        return self._to_shorts(self.user_repo.get_by_role(RoleName.TEACHER))

    def get_students_by_class(self, class_id: int) -> list[UserShort]:
        if self.school_class_repo.get_class_by_id(class_id) is None:
            raise NotFoundError(f"Класс с id={class_id} не найден")
        return self._to_shorts(self.user_repo.get_students_by_class(class_id))

    def get_students_without_class(self) -> list[UserShort]:
        return self._to_shorts(self.user_repo.get_students_without_class())

    def set_class(self, user_id: int, class_id: int | None) -> UserDetail:
        user = self._get_user(user_id)
        if user.deactivated_at is not None:
            raise BusinessValidationError("У пользователя деактивирована учетная запись!")
        self._check_class(user.role, class_id)
        updated = self.user_repo.update_user(
            user_id,
            class_id=class_id
        )
        return UserDetail.model_validate(updated)

    def remove_from_class(self, user_id: int, class_id: int) -> UserDetail:
        user = self._get_user(user_id)
        if user.class_id != class_id:
            raise BusinessValidationError("Ученик не учится в этом классе")
        return self.set_class(user_id, None)

    def update_user(self, user_id: int, data: UserUpdate) -> UserDetail:
        user = self._get_user(user_id)

        if user.role == RoleName.TEACHER and data.role != RoleName.TEACHER:
            if self._has_current_schedule(user_id):
                raise BusinessValidationError(
                    "У учителя есть уроки в расписании текущего года. Сначала замените его в расписании"
                )
        if data.role != RoleName.STUDENT and user.class_id is not None:
            raise BusinessValidationError("Сначала уберите пользователя из класса")
        
        updated = self.user_repo.update_user(
            user_id,
            last_name=data.last_name,
            first_name=data.first_name,
            middle_name=data.middle_name,
            role=data.role,
        )
        return UserDetail.model_validate(updated)

    def reset_password(self, user_id: int) -> UserCredentials:
        user = self._get_user(user_id)
        password = self._generate_password()
        self.user_repo.set_password(user_id, hash_password(password))
        return UserCredentials(id=user.id, username=user.username, password=password)

    def deactivate_user(self, user_id: int, current_user_id: int) -> UserDetail:
        user = self._get_user(user_id)
        if user_id == current_user_id:
            raise BusinessValidationError("Нельзя деактивировать самого себя")
        if user.role == RoleName.TEACHER and self._has_current_schedule(user_id):
            raise BusinessValidationError(
                "У учителя есть уроки в расписании текущего года. Сначала замените его в расписании"
            )
        return UserDetail.model_validate(self.user_repo.deactivate_user(user_id))

    def restore_user(self, user_id: int) -> UserDetail:
        self._get_user(user_id)
        return UserDetail.model_validate(self.user_repo.restore_user(user_id))

    def authenticate(self, data: UserLogin) -> UserDetail | None:
        user = self.user_repo.get_by_username(data.username)
        if user is None:
            return None
        if user.deactivated_at is not None:
            return None
        if not verify_password(data.password, user.password_hash):
            return None
        return UserDetail.model_validate(user)
