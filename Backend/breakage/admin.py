from django.contrib import admin
from .models import BreakageReport


class BreakageReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'resolved', 'timestamp')


admin.site.register(BreakageReport, BreakageReportAdmin)
