from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def role_required(*allowed_roles):
    """
    Decorator to restrict access based on user role.
    Usage: @role_required('student', 'teacher')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                # Redirect to appropriate dashboard based on role
                if request.user.is_student():
                    return redirect('student_dashboard')
                elif request.user.is_teacher():
                    return redirect('teacher_dashboard')
                elif request.user.is_department_head():
                    return redirect('department_head_dashboard')
                else:
                    return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def department_head_required(view_func):
    """Decorator to restrict access to Department Head only."""
    return role_required('department_head')(view_func)


def teacher_required(view_func):
    """Decorator to restrict access to Teacher only."""
    return role_required('teacher')(view_func)


def student_required(view_func):
    """Decorator to restrict access to Student only."""
    return role_required('student')(view_func)


