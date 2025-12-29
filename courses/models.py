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


class DepartmentProgramOutcome(models.Model):
    """
    Department-level Program Outcomes (PO).
    These are department-wide and not tied to specific courses.
    Only Department Head can create/edit department POs.
    """
    code = models.CharField(max_length=20, unique=True)  # e.g., PO1, PO2
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'code']
    
    def __str__(self):
        return f"Department {self.code}"


class DepartmentLOPOContribution(models.Model):
    """
    Mapping between Learning Outcomes (LO) and Department Program Outcomes (PO)
    with percentage contribution.
    
    Formula: PO_final_value = sum(selected_LO_student_value × LO_percentage_for_PO / 100)
    
    Example:
    - Student LO1 = 80, contribution to PO1 = 40% → 32
    - Student LO2 = 70, contribution to PO1 = 30% → 21
    - Student LO3 = 90, contribution to PO1 = 30% → 27
    - PO1 final value = 32 + 21 + 27 = 80
    """
    learning_outcome = models.ForeignKey(
        LearningOutcome, 
        on_delete=models.CASCADE, 
        related_name='department_po_contributions'
    )
    department_program_outcome = models.ForeignKey(
        DepartmentProgramOutcome,
        on_delete=models.CASCADE,
        related_name='lo_contributions'
    )
    contribution_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage contribution of this LO to the PO (0-100)"
    )
    
    class Meta:
        unique_together = [['learning_outcome', 'department_program_outcome']]
        ordering = ['department_program_outcome', 'learning_outcome']
    
    def __str__(self):
        return f"{self.learning_outcome.code} → {self.department_program_outcome.code} ({self.contribution_percentage}%)"
