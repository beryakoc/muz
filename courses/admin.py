from django.contrib import admin
from .models import Course, LearningOutcome, ProgramOutcome, LOPOMapping, Enrollment, AcademicCalendar


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'teacher', 'created_at']
    list_filter = ['created_at']
    search_fields = ['code', 'name']


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ['code', 'course', 'description', 'order']
    list_filter = ['course']
    search_fields = ['code', 'description']


@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ['code', 'course', 'description', 'order']
    list_filter = ['course']
    search_fields = ['code', 'description']


@admin.register(LOPOMapping)
class LOPOMappingAdmin(admin.ModelAdmin):
    list_display = ['learning_outcome', 'program_outcome', 'contribution_weight']
    list_filter = ['contribution_weight']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at']
    list_filter = ['course', 'enrolled_at']


@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date']
    list_filter = ['start_date']
