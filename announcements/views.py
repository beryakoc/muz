from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Announcement
from accounts.decorators import department_head_required


@department_head_required
def manage_announcements(request):
    """Department Head manages announcements."""
    announcements = Announcement.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            title = request.POST.get('title')
            content = request.POST.get('content')
            
            if title and content:
                Announcement.objects.create(
                    title=title,
                    content=content,
                    created_by=request.user
                )
                messages.success(request, 'Announcement created successfully.')
            else:
                messages.error(request, 'Title and content are required.')
        
        elif action == 'edit':
            announcement_id = request.POST.get('announcement_id')
            title = request.POST.get('title')
            content = request.POST.get('content')
            
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                announcement.title = title
                announcement.content = content
                announcement.save()
                messages.success(request, 'Announcement updated successfully.')
            except Announcement.DoesNotExist:
                messages.error(request, 'Announcement not found.')
        
        elif action == 'delete':
            announcement_id = request.POST.get('announcement_id')
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                announcement.delete()
                messages.success(request, 'Announcement deleted successfully.')
            except Announcement.DoesNotExist:
                messages.error(request, 'Announcement not found.')
        
        elif action == 'toggle':
            announcement_id = request.POST.get('announcement_id')
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                announcement.is_active = not announcement.is_active
                announcement.save()
                status = 'activated' if announcement.is_active else 'deactivated'
                messages.success(request, f'Announcement {status} successfully.')
            except Announcement.DoesNotExist:
                messages.error(request, 'Announcement not found.')
        
        return redirect('manage_announcements')
    
    return render(request, 'department_head/announcements.html', {
        'announcements': announcements,
    })
