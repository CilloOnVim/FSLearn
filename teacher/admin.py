from django.contrib import admin

from .models import TeacherProfile

# Register your models here.


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "advisory_class", "license_number")
    search_fields = ("user__last_name", "advisory_class")
