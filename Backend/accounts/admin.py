from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    is_student =  forms.BooleanField(required=False)
    is_technician = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = CustomUserForm

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher','is_technician')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
