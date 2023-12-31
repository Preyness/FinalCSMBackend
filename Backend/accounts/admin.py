from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = UserAdmin.list_display + ('is_technician', 'is_teacher')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_technician', 'is_teacher')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
