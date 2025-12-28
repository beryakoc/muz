from rest_framework import serializers
from .models import Course, LearningOutcome, ProgramOutcome, LOPOMapping, Enrollment
from accounts.serializers import UserSerializer


class LearningOutcomeSerializer(serializers.ModelSerializer):
    """Serializer for Learning Outcome."""
    class Meta:
        model = LearningOutcome
        fields = ['id', 'code', 'description', 'order', 'course']
        read_only_fields = ['id']


class ProgramOutcomeSerializer(serializers.ModelSerializer):
    """Serializer for Program Outcome."""
    class Meta:
        model = ProgramOutcome
        fields = ['id', 'code', 'description', 'order', 'course']
        read_only_fields = ['id']


class LOPOMappingSerializer(serializers.ModelSerializer):
    """Serializer for LO-PO Mapping."""
    learning_outcome_code = serializers.CharField(source='learning_outcome.code', read_only=True)
    program_outcome_code = serializers.CharField(source='program_outcome.code', read_only=True)
    
    class Meta:
        model = LOPOMapping
        fields = ['id', 'learning_outcome', 'learning_outcome_code', 
                  'program_outcome', 'program_outcome_code', 'contribution_weight']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    learning_outcomes = LearningOutcomeSerializer(many=True, read_only=True)
    program_outcomes = ProgramOutcomeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'teacher', 'teacher_name', 
                  'learning_outcomes', 'program_outcomes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'course', 'course_name', 
                  'course_code', 'enrolled_at']
        read_only_fields = ['id', 'enrolled_at']


