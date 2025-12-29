from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
from courses.models import Course, Enrollment
from .models import Assessment, AssessmentScore, AssessmentLOContribution
from accounts.decorators import teacher_required


@teacher_required
def manage_assessments(request, course_id):
    """Teacher can create/edit assessments for their courses."""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify teacher owns this course
    if course.teacher != request.user:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('teacher_courses')
    
    assessments = Assessment.objects.filter(course=course).prefetch_related('lo_contributions__learning_outcome')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            assessment_type = request.POST.get('assessment_type')
            weight_percentage = request.POST.get('weight_percentage')
            
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
                # Note: LO contributions must be set via LO-centric interface (Manage Learning Outcomes)
                messages.success(request, f'Assessment "{name}" created successfully. Use "Manage Learning Outcomes" to set LO contributions.')
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
    
    # Get LO contributions for each assessment (for display only - read-only)
    assessment_contributions = {}
    for assessment in assessments:
        contributions = AssessmentLOContribution.objects.filter(assessment=assessment).select_related('learning_outcome')
        assessment_contributions[assessment.id] = contributions
    
    return render(request, 'teacher/manage_assessments.html', {
        'course': course,
        'assessments': assessments,
        'assessment_contributions': assessment_contributions,
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
                
                score_value = request.POST.get(score_key)
                
                if score_value:
                    try:
                        score = float(score_value)
                        if score < 0 or score > 100:
                            messages.error(request, f'Score for {enrollment.student.get_full_name()} in {assessment.name} must be between 0 and 100.')
                            continue
                        
                        # Ensure score doesn't exceed 100
                        score = min(100.0, max(0.0, score))
                        
                        # Automatically calculate letter grade from numeric score
                        from assessments.utils import calculate_letter_grade
                        calculated_letter_grade = calculate_letter_grade(score)
                        
                        # Create or update score
                        score_obj, created = AssessmentScore.objects.update_or_create(
                            assessment=assessment,
                            student=enrollment.student,
                            defaults={
                                'score': score,
                                'letter_grade': calculated_letter_grade
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


@teacher_required
def manage_lo_assessments(request, course_id, lo_id):
    """
    LO-centric view: Teacher manages which assessments contribute to a specific LO.
    This is the new primary interface for setting LO-Assessment contributions.
    """
    from courses.models import LearningOutcome
    
    course = get_object_or_404(Course, id=course_id)
    learning_outcome = get_object_or_404(LearningOutcome, id=lo_id, course=course)
    
    # Verify teacher owns this course
    if course.teacher != request.user:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('teacher_courses')
    
    # Get all assessments for this course
    assessments = Assessment.objects.filter(course=course).order_by('created_at')
    
    # Get existing contributions for this LO from all assessments
    existing_contributions = AssessmentLOContribution.objects.filter(
        learning_outcome=learning_outcome
    ).select_related('assessment')
    
    # Create a dict for easy lookup: assessment_id -> contribution
    contribution_dict = {contrib.assessment.id: contrib for contrib in existing_contributions}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            # Get all assessment contributions from form
            assessment_contributions = {}
            total_percentage = Decimal('0.00')
            
            for assessment in assessments:
                contribution_key = f'assessment_{assessment.id}_contribution'
                contribution_value = request.POST.get(contribution_key, '0')
                try:
                    percentage = Decimal(str(contribution_value))
                    if percentage < 0 or percentage > 100:
                        messages.error(request, f'Contribution percentage for {assessment.name} must be between 0 and 100.')
                        return redirect('manage_lo_assessments', course_id=course_id, lo_id=lo_id)
                    assessment_contributions[assessment.id] = percentage
                    total_percentage += percentage
                except (ValueError, TypeError):
                    assessment_contributions[assessment.id] = Decimal('0.00')
            
            # Validate that sum equals 100%
            if abs(total_percentage - Decimal('100.00')) > Decimal('0.01'):  # Allow small floating point differences
                messages.error(request, f'Sum of contribution percentages must equal 100%. Current sum: {total_percentage}%')
                return redirect('manage_lo_assessments', course_id=course_id, lo_id=lo_id)
            
            # Save contributions
            with transaction.atomic():
                # Delete existing contributions for this LO
                AssessmentLOContribution.objects.filter(learning_outcome=learning_outcome).delete()
                
                # Create new contributions
                for assessment_id, percentage in assessment_contributions.items():
                    if percentage > 0:  # Only create if percentage > 0
                        assessment = Assessment.objects.get(id=assessment_id)
                        AssessmentLOContribution.objects.create(
                            assessment=assessment,
                            learning_outcome=learning_outcome,
                            contribution_percentage=percentage
                        )
            
            messages.success(request, f'Assessment contributions for {learning_outcome.code} saved successfully.')
            return redirect('manage_lo_assessments', course_id=course_id, lo_id=lo_id)
    
    return render(request, 'teacher/manage_lo_assessments.html', {
        'course': course,
        'learning_outcome': learning_outcome,
        'assessments': assessments,
        'contribution_dict': contribution_dict,
    })
