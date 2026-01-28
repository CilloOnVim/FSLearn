from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# Create your views here.


def index(request):
    return render(request, "core/index.html")

def login_view(request):
    # --- GET REQUEST ---
    if request.method == 'GET':
        role = request.GET.get('role')
        if role == 'student':
            welcome_message = "Ready to learn, Student? Log in below!"
        elif role == 'teacher':
            welcome_message = "Welcome back, Teacher! Your class awaits."
        else:
            welcome_message = "Welcome to FSLearn!"

        context = {
            'welcome_message': welcome_message,
            'form': AuthenticationForm()
        }
        return render(request, 'core/login.html', context)

    # --- POST REQUEST ---
    elif request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # --- CRITICAL REDIRECTION LOGIC ---

                # 1. CHECK TEACHER FIRST
                # We do this because your signal might have accidentally gave them
                # a StudentProfile too. The TeacherProfile is the specific one.
                # using related_name='teacher_profile'
                if hasattr(user, 'teacher_profile'):
                    return redirect('teacher:teacher_dashboard')

                # 2. CHECK STUDENT SECOND
                # using related_name='student_profile'
                elif hasattr(user, 'student_profile'):
                    return redirect('student:student_dashboard')

                # 3. ADMIN FALLBACK
                elif user.is_superuser:
                    return redirect('/admin/')

                else:
                    messages.warning(request, "Account exists but has no Student or Teacher profile.")
                    return redirect('index')

            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

        return render(request, 'core/login.html', {'form': form, 'welcome_message': 'Please try again.'})
