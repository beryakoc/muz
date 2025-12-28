from rest_framework import serializers
from .models import Assessment, AssessmentScore
from courses.serializers import LearningOutcomeSerializer


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment."""
    covered_LOs_data = LearningOutcomeSerializer(source='covered_LOs', many=True, read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Assessment
        fields = ['id', 'course', 'course_code', 'course_name', 'name', 
                  'assessment_type', 'weight_percentage', 'covered_LOs', 
                  'covered_LOs_data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssessmentScoreSerializer(serializers.ModelSerializer):
    """Serializer for Assessment Score."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    assessment_name = serializers.CharField(source='assessment.name', read_only=True)
    course_code = serializers.CharField(source='assessment.course.code', read_only=True)
    
    class Meta:
        model = AssessmentScore
        fields = ['id', 'assessment', 'assessment_name', 'course_code', 
                  'student', 'student_name', 'score', 'letter_grade', 
                  'entered_at', 'updated_at']
        read_only_fields = ['id', 'entered_at', 'updated_at']


