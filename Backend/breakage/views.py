from .serializers import BreakageReportSerializer
from .models import BreakageReport
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets


class BreakageReportViewSet(viewsets.ModelViewSet):
    # Only allow GET
    # Breakage Reports cannot be updated directly
    # Changes to the associated Equipment Instances will resolve the Breakage Report itself
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = BreakageReportSerializer
    queryset = BreakageReport.objects.all()
