from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from courses.models import Course, LearningOutcome


class Assessment(models.Model):
    """
    Assessment types: midterm, final, quiz, assignment, project, etc.
    Teachers can create assessments for their courses.
    """
    ASSESSMENT_TYPES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('other', 'Other'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weight percentage (0-100)"
    )
    covered_LOs = models.ManyToManyField(
        LearningOutcome,
        related_name='assessments',
        blank=True,
        help_text="Learning Outcomes covered by this assessment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'created_at']
    
    def __str__(self):
        return f"{self.course.code} - {self.name} ({self.weight_percentage}%)"


class AssessmentScore(models.Model):
    """
    Student scores for assessments.
    Teachers enter scores (0-100).
    """
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assessment_scores',
        limit_choices_to={'role': 'student'}
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score (0-100)"
    )
    letter_grade = models.CharField(
        max_length=2,
        choices=[
            ('AA', 'AA'),
            ('BA', 'BA'),
            ('BB', 'BB'),
            ('CB', 'CB'),
            ('CC', 'CC'),
            ('DC', 'DC'),
            ('DD', 'DD'),
            ('FF', 'FF'),
        ],
        null=True,
        blank=True,
        help_text="Letter grade for this assessment (optional)"
    )
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['assessment', 'student']]
        ordering = ['assessment', 'student']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assessment.name}: {self.score}"
