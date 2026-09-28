from Dal.database import SessionLocal
from Bll.Services.User import UserService
from Core.Enums import RoleName
from Core.Exceptions import NotFoundError

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.current_user = None
        request.is_admin = False
        request.is_teacher = False
        request.is_student = False
        user_id = request.session.get("user_id")
        if user_id:
            with SessionLocal() as session:
                service = UserService(session)
                try:
                    user = service.get_by_id(user_id)
                    if user.deactivated_at is not None:
                        # Пользователя деактивировали, пока он был в системе — выходим.
                        request.session.flush()
                    else:
                        request.current_user = user
                        request.is_admin = user.role == RoleName.ADMIN
                        request.is_teacher = user.role == RoleName.TEACHER
                        request.is_student = user.role == RoleName.STUDENT
                except NotFoundError:
                    request.session.flush()
        return self.get_response(request)
