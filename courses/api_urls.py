from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CourseViewSet, LearningOutcomeViewSet, ProgramOutcomeViewSet, LOPOMappingViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'learning-outcomes', LearningOutcomeViewSet, basename='learningoutcome')
router.register(r'program-outcomes', ProgramOutcomeViewSet, basename='programoutcome')
router.register(r'lo-po-mappings', LOPOMappingViewSet, basename='lopomapping')

urlpatterns = [
    path('', include(router.urls)),
]


