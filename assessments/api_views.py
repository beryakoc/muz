from rest_framework import viewsets, permissions
from .models import Assessment, AssessmentScore
from .serializers import AssessmentSerializer, AssessmentScoreSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assessment management."""
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Teachers can modify assessments for their courses
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class AssessmentScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for Assessment Score management."""
    queryset = AssessmentScore.objects.all()
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Teachers can enter/modify scores
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


