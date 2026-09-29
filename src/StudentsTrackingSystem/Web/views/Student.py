from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from Web.Decorators import login_required, role_required
from Dal.database import get_session
from Bll.Services.Diary import DiaryService
from Bll.Services.Schedule import ScheduleService 
from Core.Enums import RoleName, SCHOOL_DAYS_PER_WEEK, WEEKDAY_LABELS,MAX_LESSONS_PER_DAY, LESSON_TIMES
from Core.Exceptions import BllError

def get_weekdays():
    weekdays = []
    for day in range(1, SCHOOL_DAYS_PER_WEEK + 1):
        weekdays.append((day, WEEKDAY_LABELS[day]))
    return weekdays
@login_required
@role_required(RoleName.STUDENT)
def student_schedule(request):
    school_class=request.current_user.school_class
    if school_class is None:
        return redirect("student_diary")
    schedule_service=ScheduleService(db)
    with get_session() as db:
        slots=schedule_service.get_by_class(school_class.id)
        grid = {}
        for slot in slots:
            if slot.weekday not in grid:
                grid[slot.weekday] = {}
            grid[slot.weekday][slot.lesson_number] = slot
    return render(request, "schedule/by_class.html",{
        "school_class": school_class,
        "grid": grid,
        "weekdays": get_weekdays(),
        "lesson_numbers": list(range(1, MAX_LESSONS_PER_DAY + 1)),
        "lesson_times": LESSON_TIMES,
    } )
@login_required
@role_required(RoleName.STUDENT)
def student_diary(request):
    try:
        any_day=date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        any_day=date.today()
    monday=any_day-timedelta(days=any_day.weekday())
    prev_week=monday-timedelta(days=7)
    next_week=monday+timedelta(days=7)
    days=[]
    with get_session() as db:
        diary_service=DiaryService(db)
        try:
            days=diary_service.get_week(request.current_user.id, any_day)
        except BllError as e:
            messages.error(request, str(e))
    return render(request,"student/diary.html", {
        "days": days,
        "monday": monday,
        "prev_week": prev_week.isoformat(),
        "next_week": next_week.isoformat(),
        "is_current_week": monday<=date.today()<next_week,
    })

