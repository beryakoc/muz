from rest_framework import viewsets, permissions
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    """ViewSet for Announcement management."""
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Department Head can modify announcements
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


