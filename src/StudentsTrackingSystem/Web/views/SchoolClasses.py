from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from pydantic import ValidationError
from Web.Decorators import login_required, role_required
from Dal.database import get_session
from Bll.Services.SchoolClasses import SchoolClassService
from Bll.Services.SchoolYear import SchoolYearService
from Bll.Schemas.SchoolClasses import SchoolClassCreate, SchoolClassUpdate
from Bll.Services.User import UserService
from Core.Exceptions import BllError, NotFoundError
from Core.Enums import RoleName

@login_required
@role_required(RoleName.ADMIN)
def classes_root(request):
    with get_session() as db:
        year_service = SchoolYearService(db)
        current = year_service.get_current()

    if current is None:
        messages.error(request, "Текущий учебный год не установлен")
        return redirect("school_years")

    return redirect("school_classes", year_id=current.id)

@login_required
@role_required(RoleName.ADMIN)
def school_classes_list(request, year_id: int):
    with get_session() as db:
        year_service = SchoolYearService(db)
        class_service = SchoolClassService(db)

        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")

        classes = class_service.get_by_year(year_id)

    return render(request, "school_classes/list.html", {
        "year": year,
        "year_id": year_id,
        "classes": classes,
    })

@login_required
@role_required(RoleName.ADMIN)
def school_class_create(request, year_id: int):
    with get_session() as db:
        year_service = SchoolYearService(db)
        class_service = SchoolClassService(db)

        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")

        if request.method == "POST":
            try:
                data = SchoolClassCreate(
                    number=request.POST.get("number", ""),
                    letter=request.POST.get("letter", ""),
                    school_year_id=year_id,
                )
                new_class = class_service.create_class(data)
                messages.success(
                    request,
                    f"Класс {new_class.number}{new_class.letter} создан"
                )
                return redirect("school_classes", year_id=year_id)
            except ValidationError:
                messages.error(request, "Номер класса — от 1 до 11, буква — один символ")
            except BllError as e:
                messages.error(request, str(e))

        return render(request, "school_classes/form.html", {
            "action": "create",
            "year": year,
            "year_id": year_id,
            "school_class": None,
        })

@login_required
@role_required(RoleName.ADMIN)
def school_class_edit(request, year_id: int, class_id: int):
    with get_session() as db:
        class_service = SchoolClassService(db)

        try:
            school_class = class_service.get_by_id(class_id)
        except NotFoundError:
            raise Http404("Класс не найден")

        if request.method == "POST":
            try:
                data = SchoolClassUpdate(
                    number=request.POST.get("number", ""),
                    letter=request.POST.get("letter", ""),
                )
                updated = class_service.update_class(class_id, data)
                messages.success(
                    request,
                    f"Класс {updated.number}{updated.letter} обновлён"
                )
                return redirect("school_classes", year_id=year_id)
            except ValidationError:
                messages.error(request, "Номер класса — от 1 до 11, буква — один символ")
            except BllError as e:
                messages.error(request, str(e))

        return render(request, "school_classes/form.html", {
            "action": "edit",
            "year": None,
            "year_id": year_id,
            "school_class": school_class,
        })

@login_required
@role_required(RoleName.ADMIN)
def school_class_students(request, year_id: int, class_id: int):
    with get_session() as db:
        class_service = SchoolClassService(db)
        user_service = UserService(db)

        try:
            school_class = class_service.get_by_id(class_id)
        except NotFoundError:
            raise Http404("Класс не найден")
        
        students_in_class = user_service.get_students_by_class(class_id)
        students = user_service.get_students_without_class()

        return render(request, "school_classes/students.html", {
            "school_class": school_class,
            "students_in_class": students_in_class,
            "students": students,
            "year_id": year_id,
        })

@login_required
@role_required(RoleName.ADMIN)
def school_class_set_student(request, year_id: int, class_id: int, user_id: int):
    if request.method != "POST":
        raise Http404()
    
    with get_session() as db:
        service = UserService(db)
        try:
            student = service.set_class(user_id, class_id)
            messages.success(request, f"Пользователь {student.username}, успешно добавлен в класс")
        except BllError as e:
            messages.error(request, str(e))

    return redirect("school_class_students", year_id=year_id, class_id=class_id)

@login_required
@role_required(RoleName.ADMIN)
def school_class_remove_student(request, year_id: int, class_id: int, user_id: int):
    if request.method != "POST":
        raise Http404()
    
    with get_session() as db:
        service = UserService(db)
        try:
            student = service.remove_from_class(user_id, class_id)
            messages.success(request, f"Пользователь {student.username}, успешно убран из класса")
        except BllError as e:
            messages.error(request, str(e))

    return redirect("school_class_students", year_id=year_id, class_id=class_id)