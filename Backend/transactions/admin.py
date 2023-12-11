from django.contrib import admin
from .models import Transaction
from accounts.models import CustomUser


class TransactionAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "borrower":
            kwargs["queryset"] = CustomUser.objects.exclude(
                is_technician=True).exclude(is_teacher=True)
        elif db_field.name == "teacher":
            kwargs["queryset"] = CustomUser.objects.filter(is_teacher=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Transaction, TransactionAdmin)
