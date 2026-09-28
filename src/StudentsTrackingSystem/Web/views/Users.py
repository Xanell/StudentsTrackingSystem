from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from pydantic import ValidationError
from Bll.Services.User import UserService
from Bll.Schemas.User import UserCreate, UserUpdate
from Dal.database import get_session
from Core.Exceptions import BllError, NotFoundError
from Web.Decorators import login_required, role_required
from Core.Enums import RoleName, ROLE_LABELS

def get_roles():
    roles = []
    for role in RoleName:
        roles.append({"value": role.value, "label": ROLE_LABELS[role]})
    return roles

@login_required
@role_required(RoleName.ADMIN)
def users_list(request):
    with get_session() as db:
        user_service = UserService(db)
        users_list = user_service.get_all()

    return render(request, "users/list.html", {"users": users_list})

@login_required
@role_required(RoleName.ADMIN)
def user_create(request):
    with get_session() as db:
        user_service = UserService(db)

        if request.method == "POST":
            try:
                data = UserCreate(
                    first_name=request.POST.get("first_name", ""),
                    middle_name=request.POST.get("middle_name", ""),
                    last_name=request.POST.get("last_name", ""),
                    role=request.POST.get("role", ""),
                )
                created = user_service.create_user(data)
                request.session["created_user"] = {
                    "id": created.id,
                    "username": created.username,
                    "password": created.password,
                }
                return redirect("user_created")
            except ValidationError:
                messages.error(request, "Проверьте правильность заполнения полей")
            except BllError as e:
                messages.error(request, str(e))
        return render(request, "users/form.html", {
            "action": "create",
            "roles": get_roles(),
            "user": None,
        })

@login_required
@role_required(RoleName.ADMIN)
def user_created(request):
    data = request.session.pop("created_user", None)
    if data is None:
        return redirect("users")
    return render(request, "users/created.html", data)

@login_required
@role_required(RoleName.ADMIN)
def user_edit(request, user_id: int):
    with get_session() as db:
        user_service = UserService(db)

        try:
            user = user_service.get_by_id(user_id)
        except NotFoundError:
            raise Http404("Пользователь не найден")

        if request.method == "POST":
            try:
                data = UserUpdate(
                    first_name=request.POST.get("first_name", ""),
                    middle_name=request.POST.get("middle_name", ""),
                    last_name=request.POST.get("last_name", ""),
                    role=request.POST.get("role", ""),
                )
                update = user_service.update_user(user_id, data)
                messages.success(request, f"Пользователь {update.username} обновлён")
                return redirect("users")
            except ValidationError:
                messages.error(request, "Проверьте правильность заполнения полей")
            except BllError as e:
                messages.error(request, str(e))

        return render(request, "users/form.html", {
            "action": "edit",
            "user": user,
            "roles": get_roles(),
        })

@login_required
@role_required(RoleName.ADMIN)
def user_reset_password(request, user_id: int):
    if request.method != "POST":
        raise Http404()
    
    with get_session() as db:
        user_service = UserService(db)
        try:
            user_credentials = user_service.reset_password(user_id)
            request.session["created_user"] = {
                "id": user_credentials.id,
                "username": user_credentials.username,
                "password": user_credentials.password,
                "is_reset": True,
            }
        except BllError as e:
            messages.error(request, str(e))
            return redirect("users")
        return redirect("user_created")

@login_required
@role_required(RoleName.ADMIN)
def user_deactivate(request, user_id: int):
    if request.method != "POST":
        raise Http404() 

    with get_session() as db:
        user_service = UserService(db)
        try:
            user = user_service.deactivate_user(user_id, request.current_user.id)
            messages.success(request, f"Пользователь {user.last_name} {user.first_name} добавлен в архив")
        except BllError as e:
            messages.error(request, str(e))
        return redirect("users")

@login_required
@role_required(RoleName.ADMIN)
def user_archive(request):
    with get_session() as db:
        user_service = UserService(db)
        users_deactivate_list = user_service.get_inactive()

    return render(request, "users/archive.html", {"users": users_deactivate_list})

@login_required
@role_required(RoleName.ADMIN)
def user_restore(request, user_id: int):
    if request.method != "POST":
        raise Http404() 
    
    with get_session() as db:
        user_service = UserService(db)
        try:
            user = user_service.restore_user(user_id)
            messages.success(request, f"Пользователь {user.last_name} {user.first_name} восстановлен")
        except BllError as e:
            messages.error(request, str(e))
        return redirect("user_archive")