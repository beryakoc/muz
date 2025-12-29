from django.urls import path
from . import views

urlpatterns = [
    # Student views
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.student_my_courses, name='student_my_courses'),
    path('student/courses/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    
    # Teacher views
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/courses/<int:course_id>/los/', views.teacher_course_los, name='teacher_course_los'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/students/<int:student_id>/profile/', views.teacher_student_profile, name='teacher_student_profile'),
    
    # Department Head views
    path('department-head/', views.department_head_dashboard, name='department_head_dashboard'),
    path('department-head/teachers/', views.manage_teachers, name='manage_teachers'),
    path('department-head/students/', views.manage_students, name='manage_students'),
    path('department-head/courses/', views.manage_courses, name='manage_courses'),
    path('department-head/courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('department-head/assign-students/', views.assign_students, name='assign_students'),
    path('department-head/lo-po/', views.department_head_lo_po, name='department_head_lo_po'),
    path('department-head/lo-po/los/', views.department_head_manage_los, name='department_head_manage_los'),
    path('department-head/lo-po/los/<int:course_id>/', views.department_head_manage_los, name='department_head_manage_los'),
    path('department-head/lo-po/pos/', views.department_head_manage_pos, name='department_head_manage_pos'),
    path('department-head/lo-po/pos/<int:course_id>/', views.department_head_manage_pos, name='department_head_manage_pos'),
    path('department-head/po-management/', views.department_po_management, name='department_po_management'),
    path('department-head/po-management/<int:po_id>/los/', views.manage_po_lo_contributions, name='manage_po_lo_contributions'),
]


