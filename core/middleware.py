from django.utils import timezone
from datetime import timedelta

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'student_profile'):
                profile = request.user.student_profile
                now = timezone.now()
                # To reduce DB writes, only update if last_active is empty or more than 1 minute ago
                if not profile.last_active or (now - profile.last_active) > timedelta(minutes=1):
                    profile.last_active = now
                    profile.save(update_fields=['last_active'])
                
        response = self.get_response(request)
        return response
