from django.shortcuts import render, redirect
from Bll.Services.User import UserService
from Dal.database import SessionLocal
from Web.Decorators import login_required

@login_required
def home(request):
    if request.is_admin:
        return redirect("school_years")
    return render(request, "Home.html", {"user": request.current_user})