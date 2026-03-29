from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TeacherProfile

@admin.register(TeacherProfile)
class TeacherProfileAdmin(ModelAdmin):
    list_display = ('user', 'advisory_class', 'license_number')
    search_fields = ('user__first_name', 'user__last_name', 'advisory_class')