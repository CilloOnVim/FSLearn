from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from student.models import StudentProfile
from .forms import UserUpdateForm, TeacherProfileUpdateForm, StudentUserCreationForm, StudentProfileForm
from django.shortcuts import get_object_or_404


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

@login_required
def edit_profile(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    teacher = request.user.teacher_profile

    if request.method == 'POST':
        # request.FILES is mandatory for the image upload to work
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = TeacherProfileUpdateForm(request.POST, request.FILES, instance=teacher)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('teacher:teacher_dashboard') # Adjust namespace if yours isn't 'teacher'
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = TeacherProfileUpdateForm(instance=teacher)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'teacher/edit_profile.html', context)


@login_required
def my_students(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    teacher = request.user.teacher_profile
    # Pull only the students assigned to this teacher's exact class
    students = StudentProfile.objects.filter(section=teacher.advisory_class)

    if request.method == 'POST':
        u_form = StudentUserCreationForm(request.POST)
        p_form = StudentProfileForm(request.POST)

        if u_form.is_valid() and p_form.is_valid():
            # 1. Save the user object but hash the password first
            user = u_form.save(commit=False)
            user.set_password(u_form.cleaned_data['password'])
            user.save() # BOOM: Your signal just created an empty StudentProfile

            # 2. Grab that empty profile the signal just made
            student_profile = user.student_profile
            
            # 3. Populate it with the form data
            student_profile.nickname = p_form.cleaned_data['nickname']
            student_profile.level = p_form.cleaned_data['level']
            student_profile.guardian_name = p_form.cleaned_data['guardian_name']
            
            # 4. Lock the student into the teacher's class automatically
            student_profile.section = teacher.advisory_class
            
            student_profile.save()
            return redirect('teacher:my_students')
    else:
        u_form = StudentUserCreationForm()
        p_form = StudentProfileForm()

    context = {
        'teacher': teacher,
        'students': students,
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'teacher/my_students.html', context)


@login_required
def remove_student(request, student_id):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    teacher = request.user.teacher_profile
    
    # Grab the student, but ONLY if they belong to this exact teacher's class
    student_profile = get_object_or_404(StudentProfile, pk=student_id, section=teacher.advisory_class)

    if request.method == 'POST':
        # Deleting the User automatically deletes the StudentProfile due to CASCADE
        user_to_delete = student_profile.user
        user_to_delete.delete()
        
    return redirect('teacher:my_students')

@login_required
def student_progress_detail(request, student_id):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")
    
    teacher = request.user.teacher_profile
    # Ensure this student belongs to the teacher to prevent unauthorized access
    student = get_object_or_404(StudentProfile, pk=student_id, section=teacher.advisory_class)
    
    # Preload the related completions so we don't spam queries
    completed_words = student.completed_words.all().order_by('-completed_at')
    quiz_scores = student.quiz_scores.all().order_by('-completed_at')
    story_quiz_scores = student.story_quiz_scores.all().order_by('-completed_at')

    return render(request, "teacher/student_progress_detail.html", {
        "teacher": teacher,
        "student": student,
        "completed_words": completed_words,
        "quiz_scores": quiz_scores,
        "story_quiz_scores": story_quiz_scores
    })