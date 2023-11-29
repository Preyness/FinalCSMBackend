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
        many=False, slug_field='id', queryset=Transaction.objects.filter(status='RETURNED'), required=True)

    equipments = serializers.SlugRelatedField(
        many=True, slug_field='id', queryset=EquipmentInstance.objects.all())

    class Meta:
        model = BreakageReport
        fields = ['id', 'transaction', 'equipments', 'status', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def update(self, instance, validated_data):
        transaction = validated_data.get('transaction')
        equipments = validated_data.get('equipments')
        user = self.context['request'].user

        if 'transaction' in validated_data:
            raise serializers.ValidationError({
                'equipments': 'You cannot change the associated transaction for a breakage report after it has been created'
            })

        if 'equipments' in validated_data:
            raise serializers.ValidationError({
                'equipments': 'You cannot change the equipments in a breakage report after it has been created'
            })

        if not DEBUG:
            if not user.is_teacher and 'status' in validated_data and validated_data['status'] != instance.status:
                raise serializers.ValidationError(
                    "You do not have permission to change the status of a breakage report"
                )
        return super().update(instance, validated_data)

    def create(self, instance, validated_data):
        transaction = validated_data.get('transaction')
        equipments = validated_data.get('equipments')
        user = self.context['request'].user
        if transaction is None:
            raise serializers.ValidationError({
                'equipments': 'Please selected a transaction'
            })
        if equipments is None:
            raise serializers.ValidationError({
                'equipments': 'Please select equipments covered by the breakage report'
            })
        for equipment in equipments:
            if equipment not in transaction.equipments.all():
                raise serializers.ValidationError({
                    'equipments': 'All equipments must be associated with the specified transaction'
                })
        if not DEBUG:
            if not user.is_teacher and 'status' in validated_data and validated_data['status'] != instance.status:
                raise serializers.ValidationError(
                    "You do not have permission to create a breakage report"
                )
        return super().create(validated_data)
