from rest_framework import serializers
from accounts.models import CustomUser
from equipments.models import EquipmentInstance
from equipments.serializers import EquipmentInstanceSerializer
from .models import Transaction
from accounts.models import CustomUser
from config.settings import DEBUG


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    borrower = serializers.SlugRelatedField(
        many=False, slug_field='id', queryset=CustomUser.objects.all(), required=True, allow_null=True)

    equipments = serializers.SlugRelatedField(
        many=True, slug_field='id', queryset=EquipmentInstance.objects.filter(status="Working"))

    class Meta:
        model = Transaction
        fields = ['id', 'borrower', 'equipments', 'status', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def create(self, validated_data):
        user = self.context['request'].user
        if DEBUG and user.is_anonymous:
            admin = CustomUser.objects.filter(username="admin").first()
            validated_data['borrower'] = admin
        else:
            validated_data['borrower'] = user

        validated_data['status'] = 'PENDING'
        if 'equipments' in validated_data and validated_data['equipments'] == []:
            raise serializers.ValidationError(
                "You cannot create a transaction without any equipments selected"
            )

        equipments = validated_data.get('equipments', [])
        for equipment in equipments:
            equipment.status = 'Borrowed'
            equipment.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not DEBUG:
            if not user.is_teacher and 'status' in validated_data and validated_data['status'] != instance.status:
                raise serializers.ValidationError(
                    "You do not have permission to change the status of a transaction."
                )

        if 'equipments' in validated_data and instance.equipments != validated_data['equipments']:
            raise serializers.ValidationError(
                "You cannot change the equipments of an already created transaction"
            )
        if 'status' in validated_data and instance.status == 'PENDING' and validated_data['status'] == 'RETURNED':
            raise serializers.ValidationError(
                "You cannot change a PENDING transaction to RETURNED"
            )

        if 'status' in validated_data and instance.status in ['REJECTED', 'RETURNED'] and validated_data['status'] not in ['REJECTED', 'RETURNED']:
            raise serializers.ValidationError(
                "You cannot change a rejected transaction anymore"
            )

        # Check if the transaction status is being updated to RETURNED or REJECTED
        if validated_data['status'] in ['RETURNED', 'REJECTED']:
            # Get the equipment instances related to the transaction
            equipment_instances = instance.equipments.all()

            # Iterate through the equipment instances and set their status to 'Working'
            for equipment_instance in equipment_instances:
                equipment_instance.status = 'Working'
                equipment_instance.save()

        return super().update(instance, validated_data)
