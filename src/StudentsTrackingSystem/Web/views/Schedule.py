from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from pydantic import ValidationError
from Web.Decorators import login_required, role_required
from Dal.database import get_session
from Bll.Services.SchoolYear import SchoolYearService
from Bll.Services.Schedule import ScheduleService
from Bll.Services.SchoolClasses import SchoolClassService
from Bll.Services.User import UserService
from Bll.Services.Subjects import SubjectService
from Bll.Schemas.Schedule import ScheduleCreate, ScheduleUpdate
from Core.Enums import RoleName, WEEKDAY_LABELS, LESSON_TIMES, SCHOOL_DAYS_PER_WEEK, MAX_LESSONS_PER_DAY
from Core.Exceptions import NotFoundError, BllError

def get_weekdays():
    weekdays = []
    for day in range(1, SCHOOL_DAYS_PER_WEEK + 1):
        weekdays.append((day, WEEKDAY_LABELS[day]))
    return weekdays

@login_required
@role_required(RoleName.ADMIN)
def schedule_list(request):
    with get_session() as db:
        year_service = SchoolYearService(db)
        current_year = year_service.get_current()

        if current_year is None:
            messages.error(request, "Текущий учебный год не установлен")
            return render(request, "schedule/list.html", {
                "current_year": None,
                "classes": [],
            })

        class_service = SchoolClassService(db)
        classes = class_service.get_by_year(current_year.id)

    return render(request, "schedule/list.html", {
        "current_year": current_year,
        "classes": classes,
    })

@login_required
@role_required(RoleName.ADMIN)
def schedule_by_class(request, class_id: int):
    with get_session() as db:
        class_service = SchoolClassService(db)
        try:
            school_class = class_service.get_by_id(class_id)
        except NotFoundError:
            raise Http404("Класс не найден")

        service = ScheduleService(db)
        slots = service.get_by_class(class_id)

        grid = {}
        for slot in slots:
            if slot.weekday not in grid:
                grid[slot.weekday] = {}
            grid[slot.weekday][slot.lesson_number] = slot

    return render(request, "schedule/by_class.html", {
        "school_class": school_class,
        "grid": grid,
        "weekdays": get_weekdays(),
        "lesson_numbers": list(range(1, MAX_LESSONS_PER_DAY + 1)),
        "lesson_times": LESSON_TIMES,
    })

@login_required
@role_required(RoleName.ADMIN)
def schedule_by_teacher(request, teacher_id: int):
    with get_session() as db:
        user_service = UserService(db)
        try:
            teacher = user_service.get_by_id(teacher_id)
        except NotFoundError:
            raise Http404("Учитель не найден")
        if teacher.role != RoleName.TEACHER:
            raise Http404("Учитель не найден")
        service = ScheduleService(db)
        slots = service.get_by_teacher(teacher_id)

        # сетка
        grid = {}
        for slot in slots:
            if slot.weekday not in grid:
                grid[slot.weekday] = {}
            grid[slot.weekday][slot.lesson_number] = slot

    return render(request, "schedule/by_teacher.html", {
        "teacher": teacher,
        "grid": grid,
        "weekdays": get_weekdays(),
        "lesson_numbers": list(range(1, MAX_LESSONS_PER_DAY + 1)),
        "lesson_times": LESSON_TIMES,
    })

@login_required
@role_required(RoleName.ADMIN)
def schedule_create(request, class_id: int):
    with get_session() as db:
        class_service = SchoolClassService(db)
        try:
            school_class = class_service.get_by_id(class_id)
        except NotFoundError:
            raise Http404("Класс не найден")

        service = ScheduleService(db)

        if request.method == "POST":
            try:
                room = request.POST.get("room", "").strip()
                if room == "":
                    room = None
                data = ScheduleCreate(
                    class_id=class_id,
                    subject_id=request.POST.get("subject_id", ""),
                    teacher_id=request.POST.get("teacher_id", ""),
                    weekday=request.POST.get("weekday", ""),
                    lesson_number=request.POST.get("lesson_number", ""),
                    room=room,
                )
                slot = service.create_schedule(data)
                messages.success(
                    request,
                    f"✅ Урок добавлен: {slot.subject.name}, "
                    f"{WEEKDAY_LABELS[slot.weekday]}, {slot.lesson_number}-й урок"
                )
                return redirect("schedule_by_class", class_id=class_id)
            except ValidationError:
                messages.error(request, "Заполните все обязательные поля")
            except BllError as e:
                messages.error(request, str(e))

        subject_service = SubjectService(db)
        user_service = UserService(db)

        weekday_raw = request.GET.get("weekday", "")
        lesson_number_raw = request.GET.get("lesson_number", "")

        prefill = {
            "weekday": "",
            "lesson_number": "",
            "weekday_label": "",
            "lesson_time": "",
        }

        if weekday_raw and lesson_number_raw:
            try:
                weekday_int = int(weekday_raw)
                lesson_number_int = int(lesson_number_raw)

                prefill["weekday"] = weekday_int
                prefill["lesson_number"] = lesson_number_int
                prefill["weekday_label"] = WEEKDAY_LABELS.get(weekday_int, "")

                times = LESSON_TIMES.get(lesson_number_int)
                if times:
                    prefill["lesson_time"] = (
                        f"{times[0].strftime('%H:%M')}–"
                        f"{times[1].strftime('%H:%M')}"
                    )
            except (ValueError, TypeError):
                # Кривые параметры игнорируем
                pass

        return render(request, "schedule/form.html", {
            "action": "create",
            "school_class": school_class,
            "slot": None,
            "subjects": subject_service.get_all(),
            "teachers": user_service.get_by_role(RoleName.TEACHER),
            "weekdays": get_weekdays(),
            "lesson_numbers": list(range(1, MAX_LESSONS_PER_DAY + 1)),
            "lesson_times": LESSON_TIMES,
            "prefill": prefill
        })

@login_required
@role_required(RoleName.ADMIN)
def schedule_edit(request, schedule_id: int):
    with get_session() as db:
        service = ScheduleService(db)
        class_service = SchoolClassService(db)

        try:
            slot = service.get_by_id(schedule_id)
        except NotFoundError:
            raise Http404("Урок не найден")

        try:
            school_class = class_service.get_by_id(slot.class_id)
        except NotFoundError:
            raise Http404("Класс не найден")

        if request.method == "POST":
            try:
                room = request.POST.get("room", "").strip()
                if room == "":
                    room = None
                data = ScheduleUpdate(
                    subject_id=request.POST.get("subject_id", ""),
                    teacher_id=request.POST.get("teacher_id", ""),
                    weekday=request.POST.get("weekday", ""),
                    lesson_number=request.POST.get("lesson_number", ""),
                    room=room,
                )
                updated = service.update_schedule(schedule_id, data)
                messages.success(
                    request,
                    f"✅ Урок обновлён: {updated.subject.name}, "
                    f"{WEEKDAY_LABELS[updated.weekday]}, {updated.lesson_number}-й урок"
                )
                return redirect("schedule_by_class", class_id=updated.class_id)
            except ValidationError:
                messages.error(request, "Заполните все обязательные поля")
            except BllError as e:
                messages.error(request, str(e))

        subject_service = SubjectService(db)
        user_service = UserService(db)
        

        return render(request, "schedule/form.html", {
            "action": "edit",
            "school_class": school_class,
            "slot": slot,
            "subjects": subject_service.get_all(),
            "teachers": user_service.get_by_role(RoleName.TEACHER),
            "weekdays": get_weekdays(),
            "lesson_numbers": list(range(1, MAX_LESSONS_PER_DAY + 1)),
            "lesson_times": LESSON_TIMES,
            "prefill": {}
        })