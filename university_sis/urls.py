"""
URL configuration for university_sis project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def root_redirect(request):
    """Redirect root URL to login or appropriate dashboard."""
    if request.user.is_authenticated:
        if request.user.is_student():
            return redirect('student_dashboard')
        elif request.user.is_teacher():
            return redirect('teacher_dashboard')
        elif request.user.is_department_head():
            return redirect('department_head_dashboard')
    return redirect('login')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('courses.urls')),
    path('', include('assessments.urls')),
    path('', include('announcements.urls')),
    path('api/', include('accounts.api_urls')),
    path('api/', include('courses.api_urls')),
    path('api/', include('assessments.api_urls')),
    path('api/', include('announcements.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
