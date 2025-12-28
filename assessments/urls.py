from django.urls import path
from . import views

urlpatterns = [
    path('teacher/courses/<int:course_id>/assessments/', views.manage_assessments, name='manage_assessments'),
    path('teacher/courses/<int:course_id>/scores/', views.enter_scores, name='enter_scores'),
    path('teacher/courses/<int:course_id>/los/<int:lo_id>/assessments/', views.manage_lo_assessments, name='manage_lo_assessments'),
]


