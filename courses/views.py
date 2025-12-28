from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course, LearningOutcome, ProgramOutcome, LOPOMapping, Enrollment, AcademicCalendar
from accounts.decorators import role_required, department_head_required, student_required, teacher_required
from accounts.models import User
from announcements.models import Announcement
from assessments.utils import get_student_course_data


@student_required
def student_dashboard(request):
    """Student dashboard with welcome message, calendar, announcements, and assigned courses."""
    calendar_events = AcademicCalendar.objects.all()[:10]
    announcements = Announcement.objects.filter(is_active=True)[:10]
    
    # Get courses assigned to this student
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course', 'course__teacher')
    assigned_courses = [enrollment.course for enrollment in enrollments]
    
    return render(request, 'student/dashboard.html', {
        'user': request.user,
        'calendar_events': calendar_events,
        'announcements': announcements,
        'assigned_courses': assigned_courses,
    })


@student_required
def student_my_courses(request):
    """Student's enrolled courses - list view."""
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course', 'course__teacher')
    
    # Get basic info for each course
    courses_list = []
    for enrollment in enrollments:
        course = enrollment.course
        # Check if there are any grades
        from assessments.models import AssessmentScore, Assessment
        has_grades = AssessmentScore.objects.filter(
            student=request.user,
            assessment__course=course
        ).exists()
        
        courses_list.append({
            'course': course,
            'enrollment': enrollment,
            'has_grades': has_grades,
        })
    
    return render(request, 'student/my_courses.html', {
        'courses_list': courses_list,
    })


@student_required
def student_course_detail(request, course_id):
    """Student's detailed view of a specific course."""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify student is enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('student_my_courses')
    
    # Get comprehensive course data
    course_data = get_student_course_data(request.user, course)
    
    # Get all assessments (even without scores) to show structure
    from assessments.models import Assessment
    all_assessments = Assessment.objects.filter(course=course).order_by('created_at')
    
    # Create assessment list with scores and weights
    assessments_list = []
    for assessment in all_assessments:
        assessment_info = {
            'assessment': assessment,
            'score': None,
            'letter_grade': None,
            'weight': assessment.weight_percentage,
        }
        # Try to get student's score
        try:
            from assessments.models import AssessmentScore
            score_obj = AssessmentScore.objects.get(assessment=assessment, student=request.user)
            assessment_info['score'] = score_obj.score
            assessment_info['letter_grade'] = score_obj.letter_grade
        except AssessmentScore.DoesNotExist:
            pass
        assessments_list.append(assessment_info)
    
    return render(request, 'student/course_detail.html', {
        'course': course,
        'course_data': course_data,
        'assessments_list': assessments_list,
    })


@teacher_required
def teacher_dashboard(request):
    """Teacher dashboard with welcome message, calendar, announcements, and assigned students."""
    calendar_events = AcademicCalendar.objects.all()[:10]
    announcements = Announcement.objects.filter(is_active=True)[:10]
    
    # Get courses taught by this teacher with enrolled students
    courses = Course.objects.filter(teacher=request.user).prefetch_related('enrollments__student')
    courses_with_students = []
    for course in courses:
        enrollments = Enrollment.objects.filter(course=course).select_related('student')
        courses_with_students.append({
            'course': course,
            'students': [enrollment.student for enrollment in enrollments]
        })
    
    return render(request, 'teacher/dashboard.html', {
        'user': request.user,
        'calendar_events': calendar_events,
        'announcements': announcements,
        'courses_with_students': courses_with_students,
    })


@teacher_required
def teacher_courses(request):
    """Courses assigned to the teacher."""
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teacher/courses.html', {
        'courses': courses,
    })


@teacher_required
def teacher_course_los(request, course_id):
    """Teacher views Learning Outcomes for a course and manages LO-Assessment contributions."""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify teacher owns this course
    if course.teacher != request.user:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('teacher_courses')
    
    learning_outcomes = course.learning_outcomes.all()
    
    # Get contribution counts for each LO
    from assessments.models import AssessmentLOContribution
    lo_contributions = {}
    for lo in learning_outcomes:
        contributions = AssessmentLOContribution.objects.filter(learning_outcome=lo)
        lo_contributions[lo.id] = {
            'count': contributions.count(),
            'total_percentage': sum(float(c.contribution_percentage) for c in contributions)
        }
    
    return render(request, 'teacher/course_los.html', {
        'course': course,
        'learning_outcomes': learning_outcomes,
        'lo_contributions': lo_contributions,
    })


@teacher_required
def teacher_students(request):
    """Students enrolled in teacher's courses."""
    courses = Course.objects.filter(teacher=request.user).prefetch_related('enrollments__student')
    courses_with_students = []
    
    for course in courses:
        enrollments = Enrollment.objects.filter(course=course).select_related('student')
        courses_with_students.append({
            'course': course,
            'enrollments': enrollments,
        })
    
    return render(request, 'teacher/students.html', {
        'courses_with_students': courses_with_students,
    })


@teacher_required
def teacher_student_profile(request, student_id):
    """Teacher views student profile - only courses taught by this teacher."""
    from accounts.models import User
    from assessments.utils import get_student_course_data
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    # Get only courses where this teacher is the instructor and student is enrolled
    enrollments = Enrollment.objects.filter(
        student=student,
        course__teacher=request.user
    ).select_related('course', 'course__teacher')
    
    # Get course data for each enrollment
    courses_data = []
    for enrollment in enrollments:
        course = enrollment.course
        course_data = get_student_course_data(student, course)
        courses_data.append(course_data)
    
    return render(request, 'teacher/student_profile.html', {
        'student': student,
        'courses_data': courses_data,
    })


@department_head_required
def department_head_dashboard(request):
    """Department Head dashboard with welcome message, calendar, and announcements."""
    calendar_events = AcademicCalendar.objects.all()[:10]
    announcements = Announcement.objects.filter(is_active=True)[:10]
    
    return render(request, 'department_head/dashboard.html', {
        'user': request.user,
        'calendar_events': calendar_events,
        'announcements': announcements,
    })


@department_head_required
def manage_teachers(request):
    """Manage teachers - list, add, delete."""
    teachers = User.objects.filter(role='teacher')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    surname=surname,
                    role='teacher',
                    created_by=request.user
                )
                messages.success(request, f'Teacher {user.get_full_name()} created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating teacher: {str(e)}')
        
        elif action == 'delete':
            teacher_id = request.POST.get('teacher_id')
            try:
                teacher = User.objects.get(id=teacher_id, role='teacher')
                teacher.delete()
                messages.success(request, f'Teacher {teacher.get_full_name()} deleted successfully.')
            except User.DoesNotExist:
                messages.error(request, 'Teacher not found.')
        
        return redirect('manage_teachers')
    
    return render(request, 'department_head/teachers.html', {
        'teachers': teachers,
    })


@department_head_required
def manage_students(request):
    """Manage students - list, add, delete."""
    students = User.objects.filter(role='student')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    surname=surname,
                    role='student',
                    created_by=request.user
                )
                messages.success(request, f'Student {user.get_full_name()} created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating student: {str(e)}')
        
        elif action == 'delete':
            student_id = request.POST.get('student_id')
            try:
                student = User.objects.get(id=student_id, role='student')
                student.delete()
                messages.success(request, f'Student {student.get_full_name()} deleted successfully.')
            except User.DoesNotExist:
                messages.error(request, 'Student not found.')
        
        return redirect('manage_students')
    
    return render(request, 'department_head/students.html', {
        'students': students,
    })


@department_head_required
def manage_courses(request):
    """List all courses and create new ones."""
    courses = Course.objects.all().select_related('teacher')
    teachers = User.objects.filter(role='teacher')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            code = request.POST.get('code')
            name = request.POST.get('name')
            teacher_id = request.POST.get('teacher')
            
            try:
                course = Course.objects.create(
                    code=code,
                    name=name,
                    teacher=User.objects.get(id=teacher_id) if teacher_id else None
                )
                messages.success(request, f'Course {course.code} created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating course: {str(e)}')
        
        return redirect('manage_courses')
    
    return render(request, 'department_head/courses.html', {
        'courses': courses,
        'teachers': teachers,
    })


@department_head_required
def assign_students(request):
    """Department Head assigns students to courses."""
    students = User.objects.filter(role='student')
    courses = Course.objects.all()
    enrollments = Enrollment.objects.all().select_related('student', 'course')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign':
            student_id = request.POST.get('student_id')
            course_id = request.POST.get('course_id')
            
            try:
                student = User.objects.get(id=student_id, role='student')
                course = Course.objects.get(id=course_id)
                
                # Check if enrollment already exists
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course
                )
                
                if created:
                    messages.success(request, f'Student {student.get_full_name()} assigned to {course.code} successfully.')
                else:
                    messages.info(request, f'Student {student.get_full_name()} is already assigned to {course.code}.')
            except User.DoesNotExist:
                messages.error(request, 'Student not found.')
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')
            except Exception as e:
                messages.error(request, f'Error assigning student: {str(e)}')
        
        elif action == 'remove':
            enrollment_id = request.POST.get('enrollment_id')
            try:
                enrollment = Enrollment.objects.get(id=enrollment_id)
                student_name = enrollment.student.get_full_name()
                course_code = enrollment.course.code
                enrollment.delete()
                messages.success(request, f'Student {student_name} removed from {course_code} successfully.')
            except Enrollment.DoesNotExist:
                messages.error(request, 'Enrollment not found.')
        
        return redirect('assign_students')
    
    return render(request, 'department_head/assign_students.html', {
        'students': students,
        'courses': courses,
        'enrollments': enrollments,
    })


@department_head_required
def course_detail(request, course_id):
    """Course management - LO, PO, mappings."""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_lo':
            lo_code = request.POST.get('lo_code')
            lo_description = request.POST.get('lo_description')
            try:
                LearningOutcome.objects.create(
                    course=course,
                    code=lo_code,
                    description=lo_description
                )
                messages.success(request, f'Learning Outcome {lo_code} created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating LO: {str(e)}')
        
        elif action == 'delete_lo':
            lo_id = request.POST.get('lo_id')
            try:
                lo = LearningOutcome.objects.get(id=lo_id, course=course)
                lo.delete()
                messages.success(request, 'Learning Outcome deleted successfully.')
            except LearningOutcome.DoesNotExist:
                messages.error(request, 'Learning Outcome not found.')
        
        elif action == 'create_po':
            po_code = request.POST.get('po_code')
            po_description = request.POST.get('po_description')
            try:
                ProgramOutcome.objects.create(
                    course=course,
                    code=po_code,
                    description=po_description
                )
                messages.success(request, f'Program Outcome {po_code} created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating PO: {str(e)}')
        
        elif action == 'delete_po':
            po_id = request.POST.get('po_id')
            try:
                po = ProgramOutcome.objects.get(id=po_id, course=course)
                po.delete()
                messages.success(request, 'Program Outcome deleted successfully.')
            except ProgramOutcome.DoesNotExist:
                messages.error(request, 'Program Outcome not found.')
        
        elif action == 'create_mapping':
            lo_id = request.POST.get('mapping_lo')
            po_id = request.POST.get('mapping_po')
            contribution_weight = request.POST.get('contribution_weight')
            try:
                lo = LearningOutcome.objects.get(id=lo_id, course=course)
                po = ProgramOutcome.objects.get(id=po_id, course=course)
                LOPOMapping.objects.create(
                    learning_outcome=lo,
                    program_outcome=po,
                    contribution_weight=contribution_weight
                )
                messages.success(request, 'LO-PO mapping created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating mapping: {str(e)}')
        
        elif action == 'delete_mapping':
            mapping_id = request.POST.get('mapping_id')
            try:
                mapping = LOPOMapping.objects.get(id=mapping_id)
                mapping.delete()
                messages.success(request, 'LO-PO mapping deleted successfully.')
            except LOPOMapping.DoesNotExist:
                messages.error(request, 'Mapping not found.')
        
        return redirect('course_detail', course_id=course_id)
    
    learning_outcomes = LearningOutcome.objects.filter(course=course)
    program_outcomes = ProgramOutcome.objects.filter(course=course)
    lo_po_mappings = LOPOMapping.objects.filter(
        learning_outcome__course=course
    ).select_related('learning_outcome', 'program_outcome')
    
    return render(request, 'department_head/course_detail.html', {
        'course': course,
        'learning_outcomes': learning_outcomes,
        'program_outcomes': program_outcomes,
        'lo_po_mappings': lo_po_mappings,
    })
