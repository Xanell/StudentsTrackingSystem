from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from pydantic import ValidationError
from Web.Decorators import login_required, role_required
from Dal.database import get_session
from Bll.Services.SchoolYear import SchoolYearService
from Bll.Schemas.SchoolYear import SchoolYearCreate, SchoolYearUpdate
from Core.Enums import RoleName
from Core.Exceptions import BllError, NotFoundError

@login_required
@role_required(RoleName.ADMIN)
def school_years_list(request):
    with get_session() as db:
        service = SchoolYearService(db)
        years = service.get_all()
        current = service.get_current()

    return render(request, "school_years/list.html", {
        "years": years,
        "current_year": current,
    })

@login_required
@role_required(RoleName.ADMIN)
def school_year_create(request):
    with get_session() as db:
        service = SchoolYearService(db)

        if request.method == "POST":
            try:
                data = SchoolYearCreate(
                    start_date=request.POST.get("start_date", ""),
                    end_date=request.POST.get("end_date", ""),
                )
                year = service.create_school_year(data)
                messages.success(request, f"Учебный год {year.name} создан")
                return redirect("school_years")
            except ValidationError:
                messages.error(request, "Укажите даты начала и окончания")
            except BllError as e:
                messages.error(request, str(e))

        return render(request, "school_years/form.html", {
            "action": "create",
            "year": None,
        })

@login_required
@role_required(RoleName.ADMIN)
def school_year_edit(request, year_id: int):
    with get_session() as db:
        service = SchoolYearService(db)

        try:
            year = service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")

        if request.method == "POST":
            try:
                data = SchoolYearUpdate(
                    start_date=request.POST.get("start_date", ""),
                    end_date=request.POST.get("end_date", ""),
                )
                updated = service.update_year(year_id, data)
                messages.success(request, f"Учебный год {updated.name} обновлён")
                return redirect("school_years")
            except ValidationError:
                messages.error(request, "Укажите даты начала и окончания")
            except BllError as e:
                messages.error(request, str(e))

        return render(request, "school_years/form.html", {
            "action": "edit",
            "year": year,
        })

@login_required
@role_required(RoleName.ADMIN)
def school_year_make_current(request, year_id: int):
    if request.method != "POST":
        raise Http404()

    with get_session() as db:
        service = SchoolYearService(db)
        try:
            year = service.make_current(year_id)
            messages.success(request, f"Текущий год: {year.name}")
        except BllError as e:
            messages.error(request, str(e))

    return redirect("school_years")
