from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from Bll.Services.Lessons import LessonService
from Bll.Services.User import UserService
from Bll.Services.Attendance import AttendanceService
from Bll.Services.Mark import MarkService
from Bll.Services.Journal import JournalService
from Bll.Services.SchoolClasses import SchoolClassService
from Bll.Services.SchoolQuarter import SchoolQuarterService
from Bll.Schemas.Lessons import LessonUpdate
from Bll.Schemas.Attendance import AttendanceItem, AttendanceSave
from Bll.Schemas.Mark import MarkSet
from Core.Enums import RoleName, LESSON_TIMES, GradeType, GRADE_TYPE_LABELS
from pydantic import ValidationError
from Core.Exceptions import BllError, NotFoundError
from Dal.database import get_session
from Web.Decorators import login_required, role_required
from datetime import date

def get_grade_types():
    grade_types = []
    for grade in GRADE_TYPE_LABELS:
        grade_types.append({"value": grade.value, "label": GRADE_TYPE_LABELS[grade]})
    return grade_types

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
        students_service = UserService(db)
        attendance_service = AttendanceService(db)
        mark_service = MarkService(db)

        try:
            lesson = lesson_service.get_by_id(lesson_id)
        except NotFoundError:
            raise Http404("Урок не найден")

        if lesson.teacher.id != request.current_user.id:
            raise Http404("Урок не найден")
        
        start, end = LESSON_TIMES[lesson.lesson_number]
        students = students_service.get_students_by_class(lesson.school_class.id)
        attendance = attendance_service.get_by_lesson(lesson_id)
        marks = mark_service.get_by_lesson(lesson_id)

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
                lesson_service.update_lesson(lesson_id, data)

                items = []
                for student in students:
                    is_present = request.POST.get(f"present_{student.id}") is not None
                    items.append(AttendanceItem(student_id=student.id, is_present=is_present))
                attendance_service.save_for_lesson(AttendanceSave(lesson_id=lesson_id, items=items))

                existing = {}
                for mark in marks:
                    existing[(mark.student_id, mark.grade_type)] = mark

                for student in students:
                    for grade_type in GradeType:
                        value = request.POST.get(f"grade_{grade_type.value}_{student.id}", "")
                        old = existing.get((student.id, grade_type))

                        if value == "":
                            if old is not None and old.grade is not None:
                                mark_service.clear_mark(old.id)
                        else:
                            mark_service.set_mark(MarkSet(
                                lesson_id=lesson_id,
                                student_id=student.id,
                                grade_type=grade_type,
                                grade=value,
                            ))

                messages.success(request, "Урок сохранён")
                return redirect("teacher_lesson", lesson_id)
            except ValidationError:
                messages.error(request, "Проверьте тему (до 255 символов) и дату сдачи")
            except BllError as e:
                messages.error(request, str(e))

        # цикл отображения данных для отметок посещаемости 
        attendance_by_student = {}
        for record in attendance:
            attendance_by_student[record.student_id] = record
        # цикл отображения данных для оценок
        marks_by_student = {}
        for mark in marks:
            if mark.student_id not in marks_by_student:
                marks_by_student[mark.student_id] = {}
            marks_by_student[mark.student_id][mark.grade_type] = mark.grade

        rows = []
        for student in students:
            record = attendance_by_student.get(student.id)
            student_marks = marks_by_student.get(student.id, {})

            grades = []
            for grade_type in GradeType:
                grades.append({
                    "type": grade_type.value,
                    "value": student_marks.get(grade_type),
                })

            rows.append({
                "student": student,
                "is_present": record is None or record.is_present,
                "reason": record.reason if record else "",
                "grades": grades,
            })
    return render(request, "teacher/lesson_forms.html", {
        "lesson": lesson,
        "start": start,
        "end": end,
        "rows": rows,
        "grade_types": get_grade_types(),      
        "grade_values": [2, 3, 4, 5],
    })

@login_required
@role_required(RoleName.TEACHER)
def teacher_journals(request):
    with get_session() as db:
        journal_service = JournalService(db)
        teacher_id = request.current_user.id

        journals = journal_service.get_teacher_journals(teacher_id)

    return render(request, "teacher/journal_list.html", {
        "journals": journals
    })

@login_required
@role_required(RoleName.TEACHER)
def class_journal(request, class_id: int, subject_id: int):
    with get_session() as db:
        school_class_service = SchoolClassService(db)
        quarter_service = SchoolQuarterService(db)
        journal_service = JournalService(db)
        teacher_id = request.current_user.id

        allowed = False
        for link in journal_service.get_teacher_journals(teacher_id):
            if link.school_class.id == class_id and link.subject.id == subject_id:
                allowed = True
        if not allowed:
            raise Http404("Журнал не найден")
        school_class = school_class_service.get_by_id(class_id)
        quarters = quarter_service.get_by_year(school_class.school_year.id)
        if not quarters:
            messages.error(request, "Администратор ещё не задал четверти для этого года")
            return redirect("teacher_journals")

        quarter_param = request.GET.get("quarter", "")

        # Ищем такую четверть среди четвертей этого года
        selected_quarter = None
        for quarter in quarters:
            if str(quarter.id) == quarter_param:
                selected_quarter = quarter

        # Если не нашли то берем текущую 
        if selected_quarter is None:
            current = quarter_service.get_current()
            for quarter in quarters:
                if current is not None and quarter.id == current.id:
                    selected_quarter = quarter

        # Если никакую не нашли то берем первую
        if selected_quarter is None:
            selected_quarter = quarters[0]

        journal = journal_service.get_journal_for_quarter(class_id, subject_id, selected_quarter.id)
        return render(request, "teacher/journal.html", {
            "journal": journal,
            "quarters": quarters,
            "selected_quarter": selected_quarter,
            "class_id": class_id,
            "subject_id": subject_id,
        })

