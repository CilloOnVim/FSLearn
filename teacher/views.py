from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
    return render(request, "teacher/teacher_login.html")


@login_required
def teacher_dashboard(request):
    try:
        # Access the profile using the related_name 'teacher_profile'
        teacher = request.user.teacher_profile
    except AttributeError:
        # If a non-teacher tries to access this page, kick them to index
        return redirect('index')

    context = {
        'teacher': teacher,
    }
    return render(request, 'teacher/teacher_dashboard.html', context)
