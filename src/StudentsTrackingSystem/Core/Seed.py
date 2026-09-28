from sqlalchemy.orm import Session

from Core.Enums import RoleName
from Core.Security import hash_password
from Dal.Repositories.User import UserRepository

def admin_seed(session: Session, username: str = "Admin", password: str = "admin") -> None:
    """
    Создаёт единственного пользователя — администратора.
    Всё остальное (годы, четверти, классы, предметы, пользователи, расписание)
    админ заполняет через интерфейс.
    """
    user_repo = UserRepository(session)

    if user_repo.get_by_username(username) is not None:
        print(f"Администратор '{username}' уже существует.")
        return

    user_repo.create_user(
        username=username,
        password_hash=hash_password(password),
        last_name="Admin",
        first_name="Admin",
        middle_name="Admin",
        role=RoleName.ADMIN,
        class_id=None,
    )
    print(f"Создан администратор: логин '{username}', пароль '{password}'.")
