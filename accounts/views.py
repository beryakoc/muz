from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from .decorators import role_required


def login_view(request):
    """
    Login page with role selection.
    Users must select their role before logging in.
    """
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard
        if request.user.is_student():
            return redirect('student_dashboard')
        elif request.user.is_teacher():
            return redirect('teacher_dashboard')
        elif request.user.is_department_head():
            return redirect('department_head_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if not email or not password or not role:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'accounts/login.html')
        
        # Authenticate user
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(request, 'Your account is not active.')
                return render(request, 'accounts/login.html')
            
            # Verify role matches
            if user.role != role:
                messages.error(request, 'Selected role does not match your account role.')
                return render(request, 'accounts/login.html')
            
            # Check password using email
            user_auth = authenticate(request, username=email, password=password)
            if user_auth is not None:
                login(request, user_auth)
                # Redirect based on role
                if role == 'student':
                    return redirect('student_dashboard')
                elif role == 'teacher':
                    return redirect('teacher_dashboard')
                elif role == 'department_head':
                    return redirect('department_head_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    """User profile view showing name, surname, and email."""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })
