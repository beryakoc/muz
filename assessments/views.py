from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from .models import Assessment, AssessmentScore
from accounts.decorators import teacher_required


@teacher_required
def manage_assessments(request, course_id):
    """Teacher can create/edit assessments for their courses."""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify teacher owns this course
    if course.teacher != request.user:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('teacher_courses')
    
    assessments = Assessment.objects.filter(course=course).prefetch_related('covered_LOs')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            assessment_type = request.POST.get('assessment_type')
            weight_percentage = request.POST.get('weight_percentage')
            lo_ids = request.POST.getlist('covered_LOs')
            
            try:
                weight = float(weight_percentage)
                if weight < 0 or weight > 100:
                    messages.error(request, 'Weight percentage must be between 0 and 100.')
                    return redirect('manage_assessments', course_id=course_id)
                
                # Check total weight doesn't exceed 100%
                existing_assessments = Assessment.objects.filter(course=course)
                total_weight = sum(float(a.weight_percentage) for a in existing_assessments)
                if total_weight + weight > 100:
                    messages.error(request, f'Total weight would exceed 100%. Current total: {total_weight}%, Adding: {weight}%')
                    return redirect('manage_assessments', course_id=course_id)
                
                assessment = Assessment.objects.create(
                    course=course,
                    name=name,
                    assessment_type=assessment_type,
                    weight_percentage=weight
                )
                if lo_ids:
                    assessment.covered_LOs.set(lo_ids)
                messages.success(request, f'Assessment "{name}" created successfully.')
            except ValueError:
                messages.error(request, 'Invalid weight percentage value.')
            except Exception as e:
                messages.error(request, f'Error creating assessment: {str(e)}')
        
        elif action == 'delete':
            assessment_id = request.POST.get('assessment_id')
            try:
                assessment = Assessment.objects.get(id=assessment_id, course=course)
                assessment.delete()
                messages.success(request, 'Assessment deleted successfully.')
            except Assessment.DoesNotExist:
                messages.error(request, 'Assessment not found.')
        
        return redirect('manage_assessments', course_id=course_id)
    
    learning_outcomes = course.learning_outcomes.all()
    
    return render(request, 'teacher/manage_assessments.html', {
        'course': course,
        'assessments': assessments,
        'learning_outcomes': learning_outcomes,
    })


@teacher_required
def enter_scores(request, course_id):
    """Teacher enters assessment scores for students."""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify teacher owns this course
    if course.teacher != request.user:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('teacher_courses')
    
    assessments = Assessment.objects.filter(course=course)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    
    if request.method == 'POST':
        # Process all scores from the form
        for enrollment in enrollments:
            for assessment in assessments:
                score_key = f'score_{assessment.id}_{enrollment.student.id}'
                letter_grade_key = f'letter_grade_{assessment.id}_{enrollment.student.id}'
                
                score_value = request.POST.get(score_key)
                letter_grade_value = request.POST.get(letter_grade_key, '')
                
                if score_value:
                    try:
                        score = float(score_value)
                        if score < 0 or score > 100:
                            messages.error(request, f'Score for {enrollment.student.get_full_name()} in {assessment.name} must be between 0 and 100.')
                            continue
                        
                        # Ensure score doesn't exceed 100
                        score = min(100.0, max(0.0, score))
                        
                        # Create or update score
                        score_obj, created = AssessmentScore.objects.update_or_create(
                            assessment=assessment,
                            student=enrollment.student,
                            defaults={
                                'score': score,
                                'letter_grade': letter_grade_value if letter_grade_value else None
                            }
                        )
                    except Exception as e:
                        messages.error(request, f'Error saving score: {str(e)}')
        
        messages.success(request, 'Scores saved successfully.')
        return redirect('enter_scores', course_id=course_id)
    
    # Get existing scores - create a list of tuples for easier template access
    # Format: score_data = [(enrollment, [(assessment, score_obj), ...]), ...]
    score_data = []
    for enrollment in enrollments:
        student_scores = []
        for assessment in assessments:
            try:
                score_obj = AssessmentScore.objects.get(
                    assessment=assessment,
                    student=enrollment.student
                )
                student_scores.append((assessment, score_obj))
            except AssessmentScore.DoesNotExist:
                student_scores.append((assessment, None))
        score_data.append((enrollment, student_scores))
    
    return render(request, 'teacher/enter_scores.html', {
        'course': course,
        'assessments': assessments,
        'enrollments': enrollments,
        'score_data': score_data,
    })
