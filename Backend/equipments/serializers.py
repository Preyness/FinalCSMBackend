from rest_framework import serializers, exceptions
from .models import Equipment, EquipmentInstance
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from django.db.models import F
from breakages.models import BreakageReport
# -- Equipment Serializers


class EquipmentHistoricalRecordField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values('name', 'description', 'category', 'history_date', 'history_user').order_by('-history_date'))


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    date_added = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated_by = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField(
        max_length=512, required=False, allow_blank=True)

    class Meta:
        model = Equipment
        fields = ('id', 'name', 'description', 'category',
                  'last_updated', 'last_updated_by', 'date_added')
        read_only_fields = ('id', 'last_updated',
                            'last_updated_by', 'date_added')
        extra_kwargs = {"description": {"required": False, "allow_null": True}}

    def create(self, validated_data):
        user = self.context['request'].user
        # Do not allow users that are not technicians to create equipments
        if not user.is_technician:
            raise exceptions.ValidationError(
                "Non-technician users cannot create equipments")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        # Do not allow users that are not technicians to update equipments
        if not user.is_technician:
            raise exceptions.ValidationError(
                "Non-technician users cannot update equipments")
        return super().update(instance, validated_data)

    # Do not allow users that are not technicians to delete equipments
    def delete(self, instance):
        user = self.context['request'].user
        if not user.is_technician:
            raise exceptions.ValidationError(
                "Non-technician users cannot delete equipments")
        instance.delete()

    @extend_schema_field(OpenApiTypes.STR)
    def get_history_user(self, obj):
        return obj.history_user.username if obj.history_user else None

    @extend_schema_field(OpenApiTypes.STR)
    def get_last_updated_by(self, obj):
        return obj.history.first().history_user.username if obj.history.first().history_user else None


class EquipmentLogsSerializer(serializers.HyperlinkedModelSerializer):
    history_date = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    history_user = serializers.SerializerMethodField()

    class Meta:
        model = Equipment.history.model
        fields = ('history_id', 'id', 'name', 'description', 'category',
                  'history_date', 'history_user')
        read_only_fields = ('history_id', 'id', 'name', 'description',
                            'history_date', 'history_user')

    @extend_schema_field(OpenApiTypes.STR)
    def get_history_user(self, obj):
        return obj.history_user.username if obj.history_user else None


class EquipmentLogSerializer(serializers.HyperlinkedModelSerializer):
    date_added = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated_by = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    history = EquipmentHistoricalRecordField()

    class Meta:
        model = Equipment
        fields = ('id', 'name', 'description', 'category',
                  'last_updated', 'date_added', 'last_updated_by', 'history')
        read_only_fields = ('id', 'last_updated',
                            'date_added', 'last_updated_by', 'history')

    @extend_schema_field(OpenApiTypes.STR)
    def get_last_updated_by(self, obj):
        return obj.history.first().history_user.username if obj.history.first().history_user else None

# -- Equipment Instance Serializers


class EquipmentInstanceHistoricalRecordField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        data = data.annotate(equipment_name=F('equipment__name'))
        data = data.annotate(category=F('equipment__category'))
        return super().to_representation(data.values('equipment', 'equipment_name', 'category', 'status', 'remarks', 'history_date', 'history_user').order_by('-history_date'))


class EquipmentInstanceSerializer(serializers.HyperlinkedModelSerializer):
    equipment = serializers.SlugRelatedField(
        slug_field='id', queryset=Equipment.objects.all())
    equipment_name = serializers.CharField(
        source='equipment.name', read_only=True)
    category = serializers.CharField(
        source='equipment.category', read_only=True)
    status = serializers.CharField()
    remarks = serializers.CharField(
        max_length=512, required=False, allow_blank=True)
    date_added = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated_by = serializers.SerializerMethodField()
    status = serializers.ChoiceField(
        choices=EquipmentInstance.EQUIPMENT_INSTANCE_STATUS_CHOICES)

    def create(self, validated_data):
        user = self.context['request'].user
        # Do not allow users that are not technicians to create equipment instances
        if not user.is_technician:
            raise exceptions.ValidationError(
                "Non-technician users cannot create equipments")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        # Do not allow users that are not technicians to update equipment instances
        if not user.is_technician:
            raise exceptions.ValidationError(
                "Non-technician users cannot update equipment instances")
        # Forbid user from changing equipment field once the instance is already created
        # Ignore any changes to 'equipment'
        validated_data.pop('equipment', None)

        # This is for Breakage Report handling
        # First we update the EquipmentInstance
        instance = super().update(instance, validated_data)
        # Then we check if the EquipmentInstance has an associated BreakageReport which is still pending
        associated_breakage_report = BreakageReport.objects.filter(
            equipments=instance, resolved=False).first()
        # If there is one
        if associated_breakage_report:
            # Check if all the equipments of the currently associated BreakageReport are "Working"
            all_working = all(
                eq.status == 'Working' for eq in associated_breakage_report.equipments.all())

            # If all the equipments are "Working", set Breakage Report to be resolved (resolved=True)
            if all_working:
                associated_breakage_report.resolved = True
                associated_breakage_report.save()

        return instance

    # Do not allow users that are not technicians to delete equipment instances
    def delete(self, instance):
        user = self.context['request'].user
        if not user.is_technician:
            raise exceptions.ValidationError(
                "Non-technician users cannot delete equipment instances")
        instance.delete()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['equipment'] = instance.equipment.__str__()
        return representation

    class Meta:
        model = EquipmentInstance
        fields = ('id', 'equipment', 'equipment_name', 'category', 'status', 'remarks',
                  'last_updated', 'last_updated_by', 'date_added')
        read_only_fields = ('id', 'last_updated', 'equipment_name', 'category',
                            'last_updated_by', 'date_added', 'equipment_name')
        extra_kwargs = {"remarks": {"required": False, "allow_null": True}}

    @extend_schema_field(OpenApiTypes.STR)
    def get_history_user(self, obj):
        return obj.history_user.username if obj.history_user else None

    @extend_schema_field(OpenApiTypes.STR)
    def get_last_updated_by(self, obj):
        return obj.history.first().history_user.username if obj.history.first().history_user else None


class EquipmentInstanceLogsSerializer(serializers.HyperlinkedModelSerializer):
    history_date = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    history_user = serializers.SerializerMethodField()
    equipment = serializers.SlugRelatedField(
        slug_field='id', queryset=Equipment.objects.all())
    equipment_name = serializers.CharField(
        source='equipment.name', read_only=True)
    category = serializers.CharField(
        source='equipment.category', read_only=True)

    class Meta:
        model = EquipmentInstance.history.model
        fields = ('history_id', 'id', 'equipment', 'equipment_name', 'category', 'status', 'remarks',
                  'history_date', 'history_user')
        read_only_fields = ('history_id', 'id', 'equipment', 'equipment_name', 'category', 'status', 'remarks',
                            'history_date', 'history_user', 'equipment_name')

    @extend_schema_field(OpenApiTypes.STR)
    def get_history_user(self, obj):
        return obj.history_user.username if obj.history_user else None


class EquipmentInstanceLogSerializer(serializers.HyperlinkedModelSerializer):
    equipment = serializers.SlugRelatedField(
        slug_field='id', queryset=Equipment.objects.all())
    equipment_name = serializers.CharField(
        source='equipment.name', read_only=True)
    status = serializers.CharField()
    remarks = serializers.CharField()
    date_added = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated = serializers.DateTimeField(
        format="%m-%d-%Y %I:%M%p", read_only=True)
    last_updated_by = serializers.SerializerMethodField()
    history = EquipmentInstanceHistoricalRecordField()
    category = serializers.CharField(
        source='equipment.category', read_only=True)

    # Forbid user from changing equipment field once the instance is already created
    def update(self, instance, validated_data):
        # Ignore any changes to 'equipment'
        validated_data.pop('equipment', None)
        return super().update(instance, validated_data)

    class Meta:
        model = EquipmentInstance
        fields = ('id', 'equipment', 'equipment_name', 'category', 'status', 'remarks',
                  'last_updated', 'date_added', 'last_updated_by', 'history')
        read_only_fields = ('id', 'last_updated', 'equipment_name', 'category',
                            'date_added', 'last_updated_by', 'history', 'equipment_name')

    @extend_schema_field(OpenApiTypes.STR)
    def get_last_updated_by(self, obj):
        return obj.history.first().history_user.username if obj.history.first().history_user else None
