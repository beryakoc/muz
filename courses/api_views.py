from rest_framework import viewsets, permissions
from .models import Course, LearningOutcome, ProgramOutcome, LOPOMapping
from .serializers import CourseSerializer, LearningOutcomeSerializer, ProgramOutcomeSerializer, LOPOMappingSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course management."""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Department Head can modify courses
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class LearningOutcomeViewSet(viewsets.ModelViewSet):
    """ViewSet for Learning Outcome management."""
    queryset = LearningOutcome.objects.all()
    serializer_class = LearningOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Department Head can modify LO
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class ProgramOutcomeViewSet(viewsets.ModelViewSet):
    """ViewSet for Program Outcome management."""
    queryset = ProgramOutcome.objects.all()
    serializer_class = ProgramOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Department Head can modify PO
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class LOPOMappingViewSet(viewsets.ModelViewSet):
    """ViewSet for LO-PO Mapping management."""
    queryset = LOPOMapping.objects.all()
    serializer_class = LOPOMappingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Department Head can modify mappings
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


