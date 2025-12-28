from django.contrib import admin
from .models import Assessment, AssessmentScore


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'assessment_type', 'weight_percentage', 'created_at']
    list_filter = ['assessment_type', 'course']
    search_fields = ['name', 'course__code']


@admin.register(AssessmentScore)
class AssessmentScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'score', 'letter_grade', 'entered_at']
    list_filter = ['letter_grade', 'entered_at']
    search_fields = ['student__name', 'student__surname', 'assessment__name']
