from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from student.models import StudentProfile
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

@login_required
def class_progress_report(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    teacher = request.user.teacher_profile
    
    # Grab all students assigned to this teacher's specific class section
    students = StudentProfile.objects.filter(section=teacher.advisory_class).prefetch_related('completed_words', 'quiz_scores', 'story_quiz_scores')

    return render(request, "teacher/class_progress.html", {
        "teacher": teacher,
        "students": students
    })
