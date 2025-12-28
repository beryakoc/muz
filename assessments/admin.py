from django.contrib import admin
from .models import Assessment, AssessmentScore, AssessmentLOContribution


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


@admin.register(AssessmentLOContribution)
class AssessmentLOContributionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'learning_outcome', 'contribution_percentage', 'created_at']
    list_filter = ['assessment__course', 'created_at']
    search_fields = ['assessment__name', 'learning_outcome__code']
