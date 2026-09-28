from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.current_user is not None:
            return view_func(request, *args, **kwargs)
        return redirect("login")
    return wrapper

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.current_user
            if user.role not in allowed_roles:
                messages.error(request, "Доступ запрещён")
                return redirect("home")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
