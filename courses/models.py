from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class Course(models.Model):
    """
    Course model with assigned teacher.
    Only Department Head can create/edit courses.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_courses',
        limit_choices_to={'role': 'teacher'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class LearningOutcome(models.Model):
    """
    Learning Outcomes (LO) for a course.
    Only Department Head can create/edit LO.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_outcomes')
    code = models.CharField(max_length=20)  # e.g., LO1, LO2
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['course', 'order', 'code']
        unique_together = [['course', 'code']]
    
    def __str__(self):
        return f"{self.course.code} - {self.code}"


class ProgramOutcome(models.Model):
    """
    Program Outcomes (PO) for a course.
    Only Department Head can create/edit PO.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='program_outcomes')
    code = models.CharField(max_length=20)  # e.g., PO1, PO2
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['course', 'order', 'code']
        unique_together = [['course', 'code']]
    
    def __str__(self):
        return f"{self.course.code} - {self.code}"


class LOPOMapping(models.Model):
    """
    Mapping between Learning Outcomes (LO) and Program Outcomes (PO).
    Only Department Head can create/edit mappings.
    """
    CONTRIBUTION_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]
    
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, related_name='po_mappings')
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE, related_name='lo_mappings')
    contribution_weight = models.IntegerField(
        choices=CONTRIBUTION_CHOICES,
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    
    class Meta:
        unique_together = [['learning_outcome', 'program_outcome']]
        ordering = ['learning_outcome', 'program_outcome']
    
    def __str__(self):
        return f"{self.learning_outcome.code} → {self.program_outcome.code} (Weight: {self.contribution_weight})"


class Enrollment(models.Model):
    """
    Student enrollment in courses.
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['student', 'course']]
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.code}"


class AcademicCalendar(models.Model):
    """
    Academic calendar events (read-only for students/teachers, editable for Department Head).
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return self.title
