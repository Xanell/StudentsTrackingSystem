from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from Bll.Services.Lessons import LessonService
from Bll.Schemas.Lessons import LessonDetail, LessonShort, LessonUpdate
from Core.Enums import RoleName, LESSON_TIMES
from pydantic import ValidationError
from Core.Exceptions import BllError, NotFoundError
from Dal.database import get_session
from Web.Decorators import login_required, role_required
from datetime import date, datetime
@login_required
@role_required(RoleName.TEACHER)
def lessons_list(request):
    with get_session() as db:
        lesson_service = LessonService(db)
        teacher_id = request.current_user.id
        current_date = date.today()
        lessons = lesson_service.get_teacher_day(teacher_id, current_date)

        rows = []
        for lesson in lessons:
            start, end = LESSON_TIMES[lesson.lesson_number]
            rows.append({
                "lesson": lesson,
                "start": start,
                "end": end
            })

    return render(request, "teacher/lessons.html", {
        "rows": rows,
    })

@login_required
@role_required(RoleName.TEACHER)
def teacher_lesson(request, lesson_id: int):
    with get_session() as db:
        lesson_service = LessonService(db)
        try:
            lesson = lesson_service.get_by_id(lesson_id)
        except NotFoundError:
            raise Http404("Урок не найден")

        if lesson.teacher.id != request.current_user.id:
            raise Http404("Урок не найден")
        
        start, end = LESSON_TIMES[lesson.lesson_number]
        if request.method == "POST":
            try:
                topic = request.POST.get("topic", "")
                if topic == "":
                    topic = None
                homework = request.POST.get("homework", "")
                if homework == "":
                    homework = None
                homework_due_date=request.POST.get("homework_due_date", "")
                if homework_due_date == "":
                    homework_due_date = None
                data = LessonUpdate(
                    topic=topic,
                    homework=homework,
                    homework_due_date=homework_due_date
                )
                updated = lesson_service.update_lesson(lesson_id, data)
                messages.success(request, "Урок обновлен")
                return redirect("teacher_lesson", lesson_id)
            except ValidationError:
                messages.error(request, "Заполните поля")
            except BllError as e:
                messages.error(request, str(e))
    return render(request, "teacher/lesson_forms.html", {
        "lesson": lesson,
        "start": start,
        "end": end,
    })