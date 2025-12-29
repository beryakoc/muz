from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, Q
from courses.models import Course, LearningOutcome, LOPOMapping
from assessments.models import Assessment, AssessmentScore, AssessmentLOContribution


def calculate_final_lo(student, course, learning_outcome):
    """
    Calculate final LO value for a student, only if total contribution equals 100%.
    
    Business Rules:
    - Total contribution percentage from all assessments must equal exactly 100%
    - Returns None if total_contribution != 100%
    - Returns calculated LO value only if total_contribution == 100%
    - Never reads legacy/static LO value fields
    
    Formula (when total_contribution == 100%):
    LO_value = SUM( student_grade × LO_contribution_percentage / 100 )
    
    Where:
    - student_grade = student's score for that assessment (0-100)
    - LO_contribution_percentage = contribution percentage of assessment to this LO (0-100)
    
    Example:
    - Vize1: student got 80, LO contribution is 40% → 80 × 0.40 = 32
    - Vize2: student got 70, LO contribution is 40% → 70 × 0.40 = 28
    - Final: student got 90, LO contribution is 20% → 90 × 0.20 = 18
    - Final LO Value = 32 + 28 + 18 = 78
    
    Returns: Decimal between 0 and 100, or None if total_contribution != 100%
    """
    # Get all assessment-LO contributions for this LO
    contributions = AssessmentLOContribution.objects.filter(
        learning_outcome=learning_outcome,
        assessment__course=course
    ).select_related('assessment')
    
    if not contributions.exists():
        return None
    
    # Calculate total contribution percentage (sum of all contribution_percentage values)
    total_contribution = Decimal('0.00')
    for contribution in contributions:
        total_contribution += Decimal(str(contribution.contribution_percentage))
    
    # CRITICAL: Only calculate if total_contribution == 100%
    if abs(total_contribution - Decimal('100.00')) > Decimal('0.01'):  # Allow small floating point differences
        return None
    
    # Calculate LO_value: SUM( student_grade × LO_contribution_percentage / 100 )
    lo_value = Decimal('0.00')
    
    for contribution in contributions:
        assessment = contribution.assessment
        try:
            score_obj = AssessmentScore.objects.get(
                assessment=assessment,
                student=student
            )
            student_grade = Decimal(str(score_obj.score))
            lo_contribution_pct = Decimal(str(contribution.contribution_percentage))
            
            # Multiply student grade by LO contribution percentage
            # Example: 80 × 40% = 80 × 0.40 = 32
            contribution_value = student_grade * (lo_contribution_pct / Decimal('100'))
            lo_value += contribution_value
        except AssessmentScore.DoesNotExist:
            # If no score exists, contribution is 0
            continue
    
    # Ensure result is between 0 and 100
    lo_value = max(Decimal('0.00'), min(Decimal('100.00'), lo_value))
    
    return lo_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_lo_score(student, course, learning_outcome):
    """
    DEPRECATED: Use calculate_final_lo() instead.
    This function is kept for backward compatibility but delegates to calculate_final_lo().
    All new code should use calculate_final_lo() directly.
    """
    return calculate_final_lo(student, course, learning_outcome)


def calculate_course_total_grade(student, course):
    """
    Calculate total course grade using weighted average.
    
    Formula:
    Total = SUM( score_assessment * weight_percentage / 100 )
    
    Returns: Decimal between 0 and 100
    """
    assessments = Assessment.objects.filter(course=course)
    
    if not assessments.exists():
        return None
    
    total_grade = Decimal('0.00')
    total_weight = Decimal('0.00')
    
    for assessment in assessments:
        try:
            score_obj = AssessmentScore.objects.get(
                assessment=assessment,
                student=student
            )
            score = Decimal(str(score_obj.score))
            weight = Decimal(str(assessment.weight_percentage))
            
            # Add weighted contribution
            total_grade += score * (weight / Decimal('100'))
            total_weight += weight
        except AssessmentScore.DoesNotExist:
            # If no score exists, skip this assessment
            continue
    
    # If no scores exist, return None
    if total_weight == 0:
        return None
    
    # Normalize if total weight doesn't equal 100
    if total_weight != Decimal('100'):
        total_grade = total_grade * (Decimal('100') / total_weight)
    
    # Ensure result is between 0 and 100
    total_grade = max(Decimal('0.00'), min(Decimal('100.00'), total_grade))
    
    return total_grade.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_letter_grade(numeric_grade):
    """
    Convert numeric grade (0-100) to letter grade.
    
    Grading scale:
    AA: 90-100
    BA: 85-89.99
    BB: 80-84.99
    CB: 75-79.99
    CC: 70-74.99
    DC: 65-69.99
    DD: 60-64.99
    FF: 0-59.99
    """
    if numeric_grade is None:
        return None
    
    numeric_grade = Decimal(str(numeric_grade))
    
    if numeric_grade >= 90:
        return 'AA'
    elif numeric_grade >= 85:
        return 'BA'
    elif numeric_grade >= 80:
        return 'BB'
    elif numeric_grade >= 75:
        return 'CB'
    elif numeric_grade >= 70:
        return 'CC'
    elif numeric_grade >= 65:
        return 'DC'
    elif numeric_grade >= 60:
        return 'DD'
    else:
        return 'FF'


def calculate_po_achievement(student, course, program_outcome):
    """
    Calculate PO achievement value based on LO-PO mappings.
    
    PO achievement is derived from LO scores and LO-PO mapping weights.
    
    Formula:
    PO_value = weighted average of related LO scores based on contribution weights
    
    Returns: Decimal between 0 and 100
    """
    # Get all LO-PO mappings for this PO
    mappings = LOPOMapping.objects.filter(
        program_outcome=program_outcome,
        learning_outcome__course=course
    )
    
    if not mappings.exists():
        return Decimal('0.00')
    
    total_weighted_score = Decimal('0.00')
    total_weight = Decimal('0.00')
    
    for mapping in mappings:
        lo = mapping.learning_outcome
        lo_score = calculate_final_lo(student, course, lo)
        # Only include LOs where total_contribution == 100% (lo_score is not None)
        if lo_score is not None:
            contribution_weight = Decimal(str(mapping.contribution_weight))
            # Weight the LO score by contribution weight
            total_weighted_score += lo_score * contribution_weight
            total_weight += contribution_weight
    
    if total_weight == 0:
        return Decimal('0.00')
    
    # Calculate average
    po_value = total_weighted_score / total_weight
    
    # Ensure result is between 0 and 100
    po_value = max(Decimal('0.00'), min(Decimal('100.00'), po_value))
    
    return po_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_student_course_data(student, course):
    """
    Get comprehensive course data for a student including:
    - Assessment scores
    - Total course grade
    - Letter grade
    - LO achievement percentages
    - PO achievement values
    
    Returns: dict with all calculated data
    """
    data = {
        'course': course,
        'assessments': [],
        'total_grade': None,
        'letter_grade': None,
        'lo_achievements': {},
        'po_achievements': {},
    }
    
    # Get all assessments with scores
    assessments = Assessment.objects.filter(course=course).prefetch_related('scores', 'covered_LOs')
    
    for assessment in assessments:
        try:
            score_obj = AssessmentScore.objects.get(assessment=assessment, student=student)
            data['assessments'].append({
                'assessment': assessment,
                'score': score_obj.score,
                'letter_grade': score_obj.letter_grade,
            })
        except AssessmentScore.DoesNotExist:
            continue
    
    # Calculate total grade and letter grade
    total_grade = calculate_course_total_grade(student, course)
    if total_grade is not None:
        data['total_grade'] = float(total_grade)
        data['letter_grade'] = calculate_letter_grade(total_grade)
    
    # Calculate LO achievements using centralized function
    # Only include LOs where total_contribution == 100%
    learning_outcomes = LearningOutcome.objects.filter(course=course)
    for lo in learning_outcomes:
        lo_score = calculate_final_lo(student, course, lo)
        # Only add if lo_score is not None (i.e., total_contribution == 100%)
        if lo_score is not None:
            data['lo_achievements'][lo.code] = float(lo_score)
    
    # Calculate PO achievements
    program_outcomes = course.program_outcomes.all()
    for po in program_outcomes:
        po_value = calculate_po_achievement(student, course, po)
        data['po_achievements'][po.code] = float(po_value)
    
    return data


