# Register your models here.
from django.contrib import admin

from .models import FSLSign, StudentProfile


@admin.register(FSLSign)
class FSLSignAdmin(admin.ModelAdmin):
    list_display = ("char", "media_file")  # Shows these columns in the list
    search_fields = ("char",)  # Lets you search by letter


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    # These are the columns you will see in the list
    list_display = ("nickname", "level", "section", "guardian_name", "user")

    # This lets you search by the kid's name or the parent's name
    search_fields = ("nickname", "guardian_name", "user__username")

    # Filter sidebar to quickly see all "Kinder 1" students
    list_filter = ("level", "section")
