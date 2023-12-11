from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics
from .serializers import TransactionSerializer
from .models import Transaction


class TransactionViewSet(viewsets.ModelViewSet):
    # Only allow GET, POST/CREATE
    # Transactions cannot be deleted
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
