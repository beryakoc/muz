from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Course, LearningOutcome, ProgramOutcome, LOPOMapping, Enrollment, AcademicCalendar, DepartmentProgramOutcome, DepartmentLOPOContribution
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
    
    # Get department PO values for this student
    from assessments.utils import get_student_department_pos
    department_po_values = get_student_department_pos(request.user)
    
    # Get LO contribution data for PO visualization
    from courses.models import DepartmentProgramOutcome, DepartmentLOPOContribution
    from assessments.utils import calculate_final_lo
    
    po_lo_data = {}  # Store LO contributions per PO
    for po_code, po_value in department_po_values.items():
        try:
            po = DepartmentProgramOutcome.objects.get(code=po_code)
            contributions = DepartmentLOPOContribution.objects.filter(
                department_program_outcome=po
            ).select_related('learning_outcome', 'learning_outcome__course')
            
            lo_contributions = []
            for contrib in contributions:
                lo = contrib.learning_outcome
                # Only include LOs from this course
                if lo.course.id == course.id:
                    lo_score = calculate_final_lo(request.user, course, lo)
                    if lo_score is not None:
                        lo_contributions.append({
                            'lo_code': lo.code,
                            'lo_value': float(lo_score),
                            'contribution_pct': float(contrib.contribution_percentage),
                            'contributed_value': float(lo_score * (Decimal(str(contrib.contribution_percentage)) / Decimal('100')))
                        })
            
            if lo_contributions:
                po_lo_data[po_code] = {
                    'po_value': po_value,
                    'lo_contributions': lo_contributions
                }
        except DepartmentProgramOutcome.DoesNotExist:
            continue
    
    # Get comparison data for student view
    from assessments.utils import calculate_course_total_grade
    course_students = Enrollment.objects.filter(course=course).select_related('student')
    student_grades = []
    student_lo_data = {}
    
    for course_enrollment in course_students:
        other_student = course_enrollment.student
        other_grade = calculate_course_total_grade(other_student, course)
        if other_grade is not None:
            student_grades.append(float(other_grade))
        
        # Get LO achievements for comparison
        other_course_data = get_student_course_data(other_student, course)
        if other_course_data.get('lo_achievements'):
            for lo_code, lo_value in other_course_data['lo_achievements'].items():
                if lo_code not in student_lo_data:
                    student_lo_data[lo_code] = []
                student_lo_data[lo_code].append(float(lo_value))
    
    # Calculate averages - ensure we have valid data
    avg_grade = None
    if student_grades:
        valid_grades = [g for g in student_grades if g is not None]
        if valid_grades:
            avg_grade = sum(valid_grades) / len(valid_grades)
    
    avg_lo = {}
    for lo_code, values in student_lo_data.items():
        if values:
            valid_values = [v for v in values if v is not None]
            if valid_values:
                avg_lo[lo_code] = sum(valid_values) / len(valid_values)
            else:
                avg_lo[lo_code] = None
        else:
            avg_lo[lo_code] = None
    
    comparison_data = {
        'student_grade': float(course_data['total_grade']) if course_data.get('total_grade') is not None else None,
        'avg_grade': float(avg_grade) if avg_grade is not None else None,
        'lo_comparison_list': [
            {
                'lo_code': lo_code,
                'student_value': float(student_value),
                'avg_value': float(avg_lo.get(lo_code)) if avg_lo.get(lo_code) is not None else None
            }
            for lo_code, student_value in course_data.get('lo_achievements', {}).items()
            if student_value is not None
        ],
        'total_students': len([g for g in student_grades if g is not None])
    }
    
    return render(request, 'student/course_detail.html', {
        'course': course,
        'course_data': course_data,
        'assessments_list': assessments_list,
        'department_po_values': department_po_values,
        'po_lo_data': po_lo_data,
        'comparison_data': comparison_data,
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
    comparison_data = {}  # Store comparison data per course
    
    for enrollment in enrollments:
        course = enrollment.course
        course_data = get_student_course_data(student, course)
        courses_data.append(course_data)
        
        # Get all students in this course for comparison
        from assessments.utils import calculate_course_total_grade, get_student_department_pos
        from assessments.models import AssessmentScore
        
        course_students = Enrollment.objects.filter(course=course).select_related('student')
        student_grades = []
        student_lo_data = {}
        
        for course_enrollment in course_students:
            other_student = course_enrollment.student
            other_grade = calculate_course_total_grade(other_student, course)
            if other_grade is not None:
                student_grades.append({
                    'student': other_student,
                    'grade': float(other_grade)
                })
            
            # Get LO achievements for comparison
            other_course_data = get_student_course_data(other_student, course)
            if other_course_data.get('lo_achievements'):
                for lo_code, lo_value in other_course_data['lo_achievements'].items():
                    if lo_code not in student_lo_data:
                        student_lo_data[lo_code] = []
                    student_lo_data[lo_code].append(float(lo_value))
        
        # Calculate averages - ensure we have valid data
        avg_grade = None
        if student_grades:
            valid_grades = [s['grade'] for s in student_grades if s['grade'] is not None]
            if valid_grades:
                avg_grade = sum(valid_grades) / len(valid_grades)
        
        avg_lo = {}
        for lo_code, values in student_lo_data.items():
            if values:
                valid_values = [v for v in values if v is not None]
                if valid_values:
                    avg_lo[lo_code] = sum(valid_values) / len(valid_values)
                else:
                    avg_lo[lo_code] = None
            else:
                avg_lo[lo_code] = None
        
        # Create list of LO comparison data for easier template access
        lo_comparison_list = []
        for lo_code, student_lo_value in course_data.get('lo_achievements', {}).items():
            if student_lo_value is not None:
                lo_comparison_list.append({
                    'lo_code': lo_code,
                    'student_value': float(student_lo_value),
                    'avg_value': float(avg_lo.get(lo_code)) if avg_lo.get(lo_code) is not None else None
                })
        
        comparison_data[course.id] = {
            'student_grade': float(course_data['total_grade']) if course_data.get('total_grade') is not None else None,
            'avg_grade': float(avg_grade) if avg_grade is not None else None,
            'student_lo': course_data.get('lo_achievements', {}),
            'avg_lo': avg_lo,
            'lo_comparison_list': lo_comparison_list,
            'total_students': len([s for s in student_grades if s['grade'] is not None])
        }
    
    # Get department PO values for this student
    from assessments.utils import get_student_department_pos
    department_po_values = get_student_department_pos(student)
    
    # Get PO comparison data
    po_comparison = {}
    if department_po_values:
        from courses.models import DepartmentProgramOutcome, DepartmentLOPOContribution
        all_students = Enrollment.objects.filter(
            course__in=[e.course for e in enrollments]
        ).values_list('student', flat=True).distinct()
        
        for po_code, po_value in department_po_values.items():
            po_student_values = []
            for other_student_id in all_students:
                from accounts.models import User
                other_student = User.objects.get(id=other_student_id)
                other_po_values = get_student_department_pos(other_student)
                if po_code in other_po_values:
                    po_student_values.append(other_po_values[po_code])
            
            avg_po_value = None
            if po_student_values:
                valid_values = [v for v in po_student_values if v is not None]
                if valid_values:
                    avg_po_value = sum(valid_values) / len(valid_values)
            
            po_comparison[po_code] = {
                'student_value': float(po_value) if po_value is not None else None,
                'avg_value': float(avg_po_value) if avg_po_value is not None else None,
                'total_students': len([v for v in po_student_values if v is not None])
            }
    
    return render(request, 'teacher/student_profile.html', {
        'student': student,
        'courses_data': courses_data,
        'department_po_values': department_po_values,
        'comparison_data': comparison_data,
        'po_comparison': po_comparison,
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
    
    # Group enrollments by course for better organization
    enrollments_by_course = []
    course_dict = {}
    
    for enrollment in enrollments.order_by('course__code', 'student__name', 'student__surname'):
        course = enrollment.course
        if course.id not in course_dict:
            course_dict[course.id] = {
                'course': course,
                'enrollments': []
            }
        course_dict[course.id]['enrollments'].append(enrollment)
    
    # Convert to list and sort by course code
    enrollments_by_course = sorted(course_dict.values(), key=lambda x: x['course'].code)
    
    return render(request, 'department_head/assign_students.html', {
        'students': students,
        'courses': courses,
        'enrollments': enrollments,
        'enrollments_by_course': enrollments_by_course,
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
        
        return redirect('course_detail', course_id=course_id)
    
    learning_outcomes = LearningOutcome.objects.filter(course=course)
    
    return render(request, 'department_head/course_detail.html', {
        'course': course,
        'learning_outcomes': learning_outcomes,
    })


@department_head_required
def department_head_lo_po(request):
    """Department Head LO/PO management hub - shows tabs for LO and PO management."""
    courses = Course.objects.all().select_related('teacher').order_by('code')
    
    # Get LO and PO counts per course
    course_data = []
    for course in courses:
        lo_count = LearningOutcome.objects.filter(course=course).count()
        po_count = ProgramOutcome.objects.filter(course=course).count()
        course_data.append({
            'course': course,
            'lo_count': lo_count,
            'po_count': po_count,
        })
    
    return render(request, 'department_head/lo_po_management.html', {
        'course_data': course_data,
    })


@department_head_required
def department_head_manage_los(request, course_id=None):
    """Department Head manages Learning Outcomes - can override teacher changes."""
    if course_id:
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
            
            elif action == 'update_lo':
                lo_id = request.POST.get('lo_id')
                lo_code = request.POST.get('lo_code')
                lo_description = request.POST.get('lo_description')
                try:
                    lo = LearningOutcome.objects.get(id=lo_id, course=course)
                    lo.code = lo_code
                    lo.description = lo_description
                    lo.save()
                    messages.success(request, f'Learning Outcome {lo_code} updated successfully.')
                except LearningOutcome.DoesNotExist:
                    messages.error(request, 'Learning Outcome not found.')
                except Exception as e:
                    messages.error(request, f'Error updating LO: {str(e)}')
            
            elif action == 'delete_lo':
                lo_id = request.POST.get('lo_id')
                try:
                    lo = LearningOutcome.objects.get(id=lo_id, course=course)
                    lo.delete()
                    messages.success(request, 'Learning Outcome deleted successfully.')
                except LearningOutcome.DoesNotExist:
                    messages.error(request, 'Learning Outcome not found.')
            
            return redirect('department_head_manage_los', course_id=course_id)
        
        learning_outcomes = LearningOutcome.objects.filter(course=course).order_by('code')
        
        # Get contribution info for each LO
        from assessments.models import AssessmentLOContribution
        lo_contributions = {}
        for lo in learning_outcomes:
            contributions = AssessmentLOContribution.objects.filter(learning_outcome=lo)
            lo_contributions[lo.id] = {
                'count': contributions.count(),
                'total_percentage': sum(float(c.contribution_percentage) for c in contributions)
            }
        
        return render(request, 'department_head/manage_los.html', {
            'course': course,
            'learning_outcomes': learning_outcomes,
            'lo_contributions': lo_contributions,
        })
    
    # List all courses
    courses = Course.objects.all().select_related('teacher').order_by('code')
    course_data = []
    for course in courses:
        lo_count = LearningOutcome.objects.filter(course=course).count()
        course_data.append({
            'course': course,
            'lo_count': lo_count,
        })
    
    return render(request, 'department_head/manage_los_list.html', {
        'course_data': course_data,
    })


@department_head_required
def department_head_manage_pos(request, course_id=None):
    """Department Head manages Program Outcomes - can override teacher changes."""
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create_po':
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
            
            elif action == 'update_po':
                po_id = request.POST.get('po_id')
                po_code = request.POST.get('po_code')
                po_description = request.POST.get('po_description')
                try:
                    po = ProgramOutcome.objects.get(id=po_id, course=course)
                    po.code = po_code
                    po.description = po_description
                    po.save()
                    messages.success(request, f'Program Outcome {po_code} updated successfully.')
                except ProgramOutcome.DoesNotExist:
                    messages.error(request, 'Program Outcome not found.')
                except Exception as e:
                    messages.error(request, f'Error updating PO: {str(e)}')
            
            elif action == 'delete_po':
                po_id = request.POST.get('po_id')
                try:
                    po = ProgramOutcome.objects.get(id=po_id, course=course)
                    po.delete()
                    messages.success(request, 'Program Outcome deleted successfully.')
                except ProgramOutcome.DoesNotExist:
                    messages.error(request, 'Program Outcome not found.')
            
            return redirect('department_head_manage_pos', course_id=course_id)
        
        program_outcomes = ProgramOutcome.objects.filter(course=course).order_by('code')
        
        # Get mapping info for each PO
        po_mappings = {}
        for po in program_outcomes:
            mappings = LOPOMapping.objects.filter(program_outcome=po)
            po_mappings[po.id] = mappings.count()
        
        return render(request, 'department_head/manage_pos.html', {
            'course': course,
            'program_outcomes': program_outcomes,
            'po_mappings': po_mappings,
        })
    
    # List all courses
    courses = Course.objects.all().select_related('teacher').order_by('code')
    course_data = []
    for course in courses:
        po_count = ProgramOutcome.objects.filter(course=course).count()
        course_data.append({
            'course': course,
            'po_count': po_count,
        })
    
    return render(request, 'department_head/manage_pos_list.html', {
        'course_data': course_data,
    })


@department_head_required
def department_po_management(request):
    """Department Head manages department-level Program Outcomes."""
    department_pos = DepartmentProgramOutcome.objects.all().order_by('order', 'code')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_po':
            po_code = request.POST.get('po_code')
            po_description = request.POST.get('po_description')
            try:
                DepartmentProgramOutcome.objects.create(
                    code=po_code,
                    description=po_description
                )
                messages.success(request, f'Program Outcome {po_code} created successfully.')
            except Exception as e:
                messages.error(request, f'Error creating PO: {str(e)}')
        
        elif action == 'update_po':
            po_id = request.POST.get('po_id')
            po_code = request.POST.get('po_code')
            po_description = request.POST.get('po_description')
            try:
                po = DepartmentProgramOutcome.objects.get(id=po_id)
                po.code = po_code
                po.description = po_description
                po.save()
                messages.success(request, f'Program Outcome {po_code} updated successfully.')
            except DepartmentProgramOutcome.DoesNotExist:
                messages.error(request, 'Program Outcome not found.')
            except Exception as e:
                messages.error(request, f'Error updating PO: {str(e)}')
        
        elif action == 'delete_po':
            po_id = request.POST.get('po_id')
            try:
                po = DepartmentProgramOutcome.objects.get(id=po_id)
                po.delete()
                messages.success(request, 'Program Outcome deleted successfully.')
            except DepartmentProgramOutcome.DoesNotExist:
                messages.error(request, 'Program Outcome not found.')
        
        return redirect('department_po_management')
    
    # Get contribution info for each PO
    po_data = []
    for po in department_pos:
        contributions = DepartmentLOPOContribution.objects.filter(department_program_outcome=po)
        total_percentage = sum(float(c.contribution_percentage) for c in contributions)
        po_data.append({
            'po': po,
            'lo_count': contributions.count(),
            'total_percentage': total_percentage,
        })
    
    return render(request, 'department_head/department_po_management.html', {
        'po_data': po_data,
    })


@department_head_required
def manage_po_lo_contributions(request, po_id):
    """Department Head manages LO contributions for a department PO."""
    po = get_object_or_404(DepartmentProgramOutcome, id=po_id)
    
    # Get all LOs from all courses
    all_los = LearningOutcome.objects.all().select_related('course').order_by('course__code', 'code')
    
    # Get existing contributions for this PO
    existing_contributions = DepartmentLOPOContribution.objects.filter(
        department_program_outcome=po
    ).select_related('learning_outcome', 'learning_outcome__course')
    
    # Create a dict for quick lookup
    contribution_dict = {contrib.learning_outcome.id: contrib for contrib in existing_contributions}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_contributions':
            # Delete all existing contributions
            existing_contributions.delete()
            
            # Get all LO IDs and percentages from form
            lo_ids = request.POST.getlist('lo_id')
            percentages = request.POST.getlist('percentage')
            
            # Validate total percentage
            total_percentage = sum(float(p) for p in percentages if p)
            
            if abs(total_percentage - 100.0) > 0.01:
                messages.error(request, f'Total contribution percentage must equal 100%. Current total: {total_percentage:.2f}%')
                return redirect('manage_po_lo_contributions', po_id=po_id)
            
            # Create new contributions
            for lo_id, percentage in zip(lo_ids, percentages):
                if lo_id and percentage and float(percentage) > 0:
                    try:
                        lo = LearningOutcome.objects.get(id=lo_id)
                        DepartmentLOPOContribution.objects.create(
                            learning_outcome=lo,
                            department_program_outcome=po,
                            contribution_percentage=float(percentage)
                        )
                    except LearningOutcome.DoesNotExist:
                        continue
                    except Exception as e:
                        messages.error(request, f'Error creating contribution: {str(e)}')
            
            messages.success(request, f'LO contributions for {po.code} saved successfully.')
            return redirect('manage_po_lo_contributions', po_id=po_id)
        
        elif action == 'remove_contribution':
            contrib_id = request.POST.get('contrib_id')
            try:
                contrib = DepartmentLOPOContribution.objects.get(id=contrib_id, department_program_outcome=po)
                contrib.delete()
                messages.success(request, 'Contribution removed successfully.')
            except DepartmentLOPOContribution.DoesNotExist:
                messages.error(request, 'Contribution not found.')
            
            return redirect('manage_po_lo_contributions', po_id=po_id)
    
    # Calculate total percentage
    total_percentage = sum(float(c.contribution_percentage) for c in existing_contributions)
    
    return render(request, 'department_head/manage_po_lo_contributions.html', {
        'po': po,
        'all_los': all_los,
        'existing_contributions': existing_contributions,
        'contribution_dict': contribution_dict,
        'total_percentage': total_percentage,
    })
