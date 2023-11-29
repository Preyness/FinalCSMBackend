from rest_framework import viewsets
from .models import BreakageReport
from .serializers import BreakageReportSerializer
from rest_framework.permissions import IsAuthenticated
from config.settings import DEBUG

# Create your views here.


class BreakageReportViewSet(viewsets.ModelViewSet):
    if (not DEBUG):
        permission_classes = [IsAuthenticated]
    serializer_class = BreakageReportSerializer
    queryset = BreakageReport.objects.all()
