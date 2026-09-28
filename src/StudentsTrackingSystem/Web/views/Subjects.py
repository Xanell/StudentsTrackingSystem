from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from pydantic import ValidationError
from Web.Decorators import login_required, role_required
from Dal.database import get_session
from Bll.Services.Subjects import SubjectService
from Bll.Schemas.Subject import SubjectCreate, SubjectUpdate
from Core.Enums import RoleName
from Core.Exceptions import BllError, NotFoundError

@login_required
@role_required(RoleName.ADMIN)
def subject_list(request):
    with get_session() as db:
        service = SubjectService(db)
        subjects = service.get_all()

    return render(request, "subjects/list.html", {
        "subjects": subjects
    })

@login_required
@role_required(RoleName.ADMIN)
def subject_create(request):
    with get_session() as db:
        service = SubjectService(db)
        if request.method == "POST":
            try:
                short_name=request.POST.get("short_name", "").strip()
                if short_name == "":
                    short_name = None
                data = SubjectCreate(
                    name=request.POST.get("name", ""),
                    short_name=short_name,
                )

                subject = service.create_subject(data)
                messages.success(request, f"Предмет {subject.name} создан")
                return redirect("subjects")
            except ValidationError:
                messages.error(request, "Укажите название предмета")
            except BllError as e:
                messages.error(request, str(e))
        return render(request, "subjects/form.html",{
            "action": "create",
            "subject": None
        })

@login_required
@role_required(RoleName.ADMIN)
def subject_edit(request, subject_id: int):
    with get_session() as db:
        service = SubjectService(db)

        try:
            subject = service.get_by_id(subject_id)
        except NotFoundError:
            raise Http404("Предмет не найден")

        if request.method == "POST":
            try:
                short_name=request.POST.get("short_name", "").strip()
                if short_name == "":
                    short_name = None
                data = SubjectUpdate(
                    name=request.POST.get("name", ""),
                    short_name=short_name
                )
                updated = service.update_subject(subject_id, data)
                messages.success(request, f"Предмет {updated.name} обновлен")
                return redirect("subjects")
            except ValidationError:
                messages.error(request, "Укажите название предмета")
            except BllError as e:
                messages.error(request, str(e))
        return render(request, "subjects/form.html", {
            "action": "edit",
            "subject": subject
        })
