from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import TransactionSerializer
from .models import Transaction
from config.settings import DEBUG


class TransactionViewSet(viewsets.ModelViewSet):
    if (not DEBUG):
        permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
