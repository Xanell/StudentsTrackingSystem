from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from pydantic import ValidationError
from Web.Decorators import login_required, role_required
from Dal.database import get_session
from Bll.Services.SchoolQuarter import SchoolQuarterService
from Bll.Services.DayOff import DayOffService
from Bll.Services.SchoolYear import SchoolYearService
from Bll.Schemas.SchoolQuarter import SchoolQuarterCreate, SchoolQuarterUpdate
from Bll.Schemas.DayOff import DayOffCreate, DayOffUpdate
from Core.Exceptions import BllError, NotFoundError
from Core.Enums import DAY_OFF_TYPES, DAY_TYPE_LABELS, RoleName

def get_day_types():
    day_types = []
    for day in DAY_OFF_TYPES:
        day_types.append({"value": day.value, "label": DAY_TYPE_LABELS[day]})
    return day_types

@login_required
@role_required(RoleName.ADMIN)
def calendar_root(request):
    with get_session() as db:
        year_service = SchoolYearService(db)
        current = year_service.get_current()

    if current is None:
        messages.error(request, "Текущий учебный год не установлен")
        return redirect("school_years")

    return redirect("school_calendar", year_id=current.id)

@login_required
@role_required(RoleName.ADMIN)
def school_calendar_list(request, year_id: int):
    with get_session() as db:
        quarter_service = SchoolQuarterService(db)
        year_service = SchoolYearService(db)
        dayoff_service = DayOffService(db)

        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")

        quarters = quarter_service.get_by_year(year_id)
        daysoff = dayoff_service.get_by_year(year_id)

    return render(request, "school_calendar/list.html", {
        "year": year,
        "year_id": year_id,
        "quarters": quarters,
        "daysoff": daysoff
    })

@login_required
@role_required(RoleName.ADMIN)
def quarter_add(request, year_id: int):
    with get_session() as db:
        quarter_service = SchoolQuarterService(db)
        year_service = SchoolYearService(db)

        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")

        if request.method == "POST":
            try:
                data = SchoolQuarterCreate(
                    school_year_id=year_id,
                    number=request.POST.get("number", ""),
                    start_date=request.POST.get("start_date", ""),
                    end_date=request.POST.get("end_date", ""),
                )
                created = quarter_service.create_quarter(data)
                messages.success(request, f"Новая четверть {created.number} создана")
                return redirect("school_calendar", year_id=year_id)
            except ValidationError:
                messages.error(request, "Ошибка")
            except BllError as e:
                messages.error(request, str(e))
    return render(request, "school_calendar/quarter_form.html", {
        "action": "create",
        "year": year,
        "year_id": year_id,
        "quarter": None,
    })

@login_required
@role_required(RoleName.ADMIN)
def quarter_edit(request, year_id: int, quarter_id: int):
    with get_session() as db:
        quarter_service = SchoolQuarterService(db)
        year_service = SchoolYearService(db)
        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")
        try:
            quarter = quarter_service.get_by_id(quarter_id)
        except NotFoundError:
            raise Http404("Четверть не найдена")
        if quarter.school_year_id != year_id:
            raise Http404("Четверть не найдена")

        if request.method == "POST":
            try:
                data = SchoolQuarterUpdate(
                    start_date=request.POST.get("start_date", ""),
                    end_date=request.POST.get("end_date", "")
                )
                quarter_service.update_quarter(quarter_id, data)
                messages.success(request, f"Четверть {quarter.number} обновлена")
                return redirect("school_calendar", year_id=year_id)
            except ValidationError:
                messages.error(request, "Неверные даты")
            except BllError as e:
                messages.error(request, str(e))
    return render(request, "school_calendar/quarter_form.html",{
        "action": "edit",
        "year_id": year_id,
        "quarter": quarter,
        "year": year
    })

@login_required
@role_required(RoleName.ADMIN)
def dayoff_add(request, year_id: int):
    with get_session() as db:
        dayoff_service = DayOffService(db)
        year_service = SchoolYearService(db)
        
        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")

        if request.method == "POST":
            try:
                start_date = request.POST.get("start_date", "")
                end_date=request.POST.get("end_date", "")
                if end_date == "":
                    end_date = start_date
                data = DayOffCreate(
                    school_year_id=year_id,
                    start_date=start_date,
                    end_date=end_date,
                    day_type=request.POST.get("day_type", ""),
                    title=request.POST.get("title", ""),
                )
                created = dayoff_service.create_day_off(data)
                messages.success(request, f"День {created.title} добавлен в календарь")
                return redirect("school_calendar", year_id=year_id)
            except ValidationError:
                messages.error(request, "Укажите даты, тип, название")
            except BllError as e:
                messages.error(request, str(e))
    return render(request, "school_calendar/dayoff_form.html",{
        "action": "create",
        "year_id": year_id,
        "dayoff": None,
        "year": year,
        "day_types": get_day_types(),
    })

@login_required
@role_required(RoleName.ADMIN)
def dayoff_edit(request, year_id: int, day_id: int):
    with get_session() as db:
        dayoff_service = DayOffService(db)
        year_service = SchoolYearService(db)
        try:
            year = year_service.get_by_id(year_id)
        except NotFoundError:
            raise Http404("Учебный год не найден")
        try:
            dayoff = dayoff_service.get_by_id(day_id)
        except NotFoundError:
            raise Http404("День не найден")
        if dayoff.school_year_id != year_id:
            raise Http404("День не найдена")

        if request.method == "POST":
            try:
                start_date = request.POST.get("start_date", "")
                end_date=request.POST.get("end_date", "")
                if end_date == "":
                    end_date = start_date
                data = DayOffUpdate(
                    start_date=start_date,
                    end_date=end_date,
                    day_type=request.POST.get("day_type", ""),
                    title=request.POST.get("title", ""),
                )
                updated = dayoff_service.update_day_off(day_id, data)
                messages.success(request, f"День {updated.title} обновлен")
                return redirect("school_calendar", year_id=year_id)
            except ValidationError:
                messages.error(request, "Укажите даты, тип, название")
            except BllError as e:
                messages.error(request, str(e))
    return render(request, "school_calendar/dayoff_form.html",{
        "action": "edit",
        "year_id": year_id,
        "dayoff": dayoff,
        "year": year,
        "day_types": get_day_types(),
    })