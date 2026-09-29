from django.shortcuts import render, redirect
from Web.Decorators import login_required

@login_required
def home(request):
    if request.is_admin:
        return redirect("school_years")
    if request.is_teacher:
        return redirect("lessons_by_day")
    if request.is_student:
        return redirect("student_diary")
    return render(request, "Home.html", {"user": request.current_user})