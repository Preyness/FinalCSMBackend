from rest_framework import serializers
from accounts.models import CustomUser
from equipments.models import EquipmentInstance
from equipments.serializers import EquipmentInstanceSerializer
from .models import Transaction
from accounts.models import CustomUser
from config.settings import DEBUG
from .models import BreakageReport


class BreakageReportSerializer(serializers.HyperlinkedModelSerializer):
    transaction = serializers.SlugRelatedField(
        many=False, slug_field='id', queryset=Transaction.objects.all(), required=True)

    equipments = serializers.SlugRelatedField(
        many=True, slug_field='id', queryset=EquipmentInstance.objects.all())

    class Meta:
        model = BreakageReport
        fields = ['id', 'transaction', 'equipments', 'resolved', 'timestamp']
        read_only_fields = ['id', 'transaction',
                            'equipments', 'resolved', 'timestamp']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['equipments'] = [
            eq.__str__() for eq in instance.equipments.all()]
        return representation
