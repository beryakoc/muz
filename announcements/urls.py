from django.urls import path
from . import views

urlpatterns = [
    path('department-head/announcements/', views.manage_announcements, name='manage_announcements'),
]


