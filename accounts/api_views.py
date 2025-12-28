from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from .decorators import department_head_required


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    Only Department Head can create users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            # Only Department Head can create/update/delete users
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        # Only Department Head can create users
        if not self.request.user.is_department_head():
            raise permissions.PermissionDenied("Only Department Head can create users.")
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def students(self, request):
        """Get all students."""
        students = User.objects.filter(role='student')
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def teachers(self, request):
        """Get all teachers."""
        teachers = User.objects.filter(role='teacher')
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)


