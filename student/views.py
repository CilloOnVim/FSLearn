# Create your views here.
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import FSLSign


def translator_view(request):
    # Fetch all signs from the DB
    signs = FSLSign.objects.all()

    # Create a dictionary: {'a': '/media/fsl_clips/a.png', 'b': ...}
    # We lower() the char to make matching easier later
    sign_map = {sign.char.lower(): sign.media_file.url for sign in signs}

    context = {
        "sign_map": json.dumps(sign_map)  # Pass this to the template as a JSON string
    }
    return render(request, "student/fsl_translator.html", context)

@login_required
def student_dashboard(request):
    try:
        # Access the profile using the related_name 'student_profile'
        student = request.user.student_profile
    except AttributeError:
        # If they logged in but don't have a student profile, kick them out.
        # This prevents the page from crashing with a 500 error.
        return redirect('index')

    context = {
        'student': student,
    }
    return render(request, 'student/student_dashboard.html', context)
