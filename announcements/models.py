from django.db import models
from accounts.models import User


class Announcement(models.Model):
    """
    Announcements that can be created/edited/deleted only by Department Head.
    All users can view announcements.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements',
        limit_choices_to={'role': 'department_head'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
