from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AssessmentViewSet, AssessmentScoreViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'assessment-scores', AssessmentScoreViewSet, basename='assessmentscore')

urlpatterns = [
    path('', include(router.urls)),
]


