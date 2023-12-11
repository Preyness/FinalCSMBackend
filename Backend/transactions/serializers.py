from rest_framework import serializers, exceptions
from accounts.models import CustomUser
from equipments.models import EquipmentInstance
from .models import Transaction
from breakage.models import BreakageReport
from accounts.models import CustomUser
from config.settings import DEBUG


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    borrower = serializers.SlugRelatedField(
        many=False, slug_field='id', queryset=CustomUser.objects.all(), required=False, allow_null=True)

    equipments = serializers.SlugRelatedField(
        many=True, slug_field='id', queryset=EquipmentInstance.objects.filter(status="Working"), required=False)

    transaction_status = serializers.ChoiceField(
        choices=Transaction.TRANSACTION_STATUS_CHOICES)

    class Meta:
        model = Transaction
        fields = ['id', 'borrower', 'teacher',
                  'equipments', 'transaction_status', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    # Do not allow deletion of transactions
    def delete(self):
        raise exceptions.ValidationError(
            "Deletion of transactions is not allowed. Please opt to cancel a transaction or finalize it")

    def create(self, validated_data):
        # Any transactions created will be associated with the one sending the POST/CREATE request
        user = self.context['request'].user
        validated_data.data['borrower'] = user

        # All created transactions will be labelled as Pending
        validated_data['transaction_status'] = 'Pending'

        # If no teacher responsible for the borrow transaction is selected, raise an error
        if 'teacher' not in validated_data:
            raise serializers.ValidationError(
                "You have not selected a teacher responsible for your borrow transaction")

        # If no borrower responsible for the borrow transaction is selected, raise an error
        if 'borrower' not in validated_data:
            raise serializers.ValidationError(
                "No borrower assigned for this transaction!")

        # If the user in the teacher field is not actually a teacher, raise an error
        borrower = validated_data.get('borrower')
        if borrower and borrower.is_teacher or borrower.is_technician:
            raise serializers.ValidationError(
                "The borrower must be a student. Not a teacher or techician")

        # If the user in the teacher field is not actually a teacher, raise an error
        teacher = validated_data.get('teacher')
        if teacher and not teacher.is_teacher:
            raise serializers.ValidationError(
                "The assigned teacher is not a valid teacher")

        # If the user in the teacher field is not actually a teacher, raise an error
        teacher = validated_data.get('teacher')
        if teacher and not teacher.is_teacher:
            raise serializers.ValidationError(
                "The specified user is not a teacher.")

        # If there are no equipments specified, raise an error
        if 'equipments' in validated_data and validated_data['equipments'] == []:
            raise serializers.ValidationError(
                "You cannot create a transaction without any equipments selected"
            )

       # Check if any of the equipment instances are already in a non-finalized transaction
        equipments = validated_data['equipments']
        for equipment in equipments:
            existing__pending_transactions = Transaction.objects.filter(
                equipments=equipment, status__in=['Pending', 'Approved', 'Borrowed', 'With Breakage: Pending Resolution'])
            if existing__pending_transactions.exists():
                raise serializers.ValidationError(
                    f"Cannot add Equipment #{equipment.id}. It is still part of a non-finalized transaction")

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # If user is not a teacher or a technician, forbid them from changing the status of a transaction
        if not user.is_teacher and not user.technician and 'transaction_status' in validated_data and validated_data['transaction_status'] != instance.status:
            raise serializers.ValidationError(
                "You are not a teacher or technician. You do not have permission to change the status of transactions"
            )

        # If user is not a teacher, forbid them from changing the status of a transaction
        if not user.is_teacher and 'transaction_status' in validated_data and validated_data['transaction_status'] != instance.status:
            raise serializers.ValidationError(
                "You do not have permission to change the status of a transaction"
            )
        # Do not allow changes to equipments on created transactions
        if 'equipments' in validated_data and instance.equipments != validated_data['equipments']:
            raise serializers.ValidationError(
                "You cannot change the equipments of an already created transaction"
            )

        # For already finalized/done transactions (Rejected or Finalized ones)
        # Do not allow any changes to already finalized transactions
        if instance.status in ['Rejected', 'Finalized']:
            raise serializers.ValidationError(
                "Unable to update rejected or finalized transaction. Please create a new one"
            )

        # Check if the update involves the transaction status
        if 'transaction_status' in validated_data:

            # For Pending transactions
            # If not changing to Approved or Rejected, throw an error
            if instance.status == 'Pending' and validated_data['transaction_status'] != 'Approved' or validated_data['transaction_status'] != 'Rejected':
                raise serializers.ValidationError(
                    "A pending transaction can only change to Approved or Rejected"
                )

            # For Approved transactions,
            # If not changing to Borrowed or Cancelled, throw an error
            # Already approved transactions can only be moved to Borrowed or Cancelled
            if instance.status == 'Approved' and validated_data['transaction_status'] != 'Borrowed' or validated_data != 'Cancelled':
                raise serializers.ValidationError(
                    "An already approved transaction can only changed to Borrowed (On borrow) or Cancelled"
                )

            # For Borrowed transactions,
            # If not changing to returned, throw an error
            # Borrowed transactions that can only be changed to returned, pending checking for broken items
            if instance.status == 'Borrowed' and validated_data['transaction_status'] != 'Finalized' or validated_data != 'With Breakage: Pending Resolution':
                raise serializers.ValidationError(
                    "A borrowed transaction can only changed to status of Finalized or With Breakage: Pending Resolution"
                )

            # For Return: Pending Checking transactions,
            # If not changing to With Breakages: Pending Resolution or Finalized, throw an error
            # Returned transactions can only be finalized without any issues or be marked as with breakages
            if instance.status == 'Returned: Pending Checking' and validated_data['transaction_status'] != 'Finalized' or validated_data != 'With Breakage: Pending Resolution':
                raise serializers.ValidationError(
                    "A borrowed transaction can only changed to status of Finalized or With Breakage: Pending Resolution"
                )

            # For transactions with pending breakage resolutions,
            # Do not allow updating of status. It should be updated within its respective breakage report
            # If it has been resolved there, this field will automatically update to Finalized
            if instance.status == 'With Breakage: Pending Resolution':
                raise serializers.ValidationError(
                    "A transaction with pending breakage resolutions must be updated or resolved in its respective breakage report"
                )

            # If there are no issues and a transaction changes from Approved to Borrowed, label the selected equipment's statuses as Borrowed
            if instance.status == 'Approved' and validated_data['transaction_status'] == 'Borrowed':
                equipments = validated_data.get('equipments', [])
                for equipment in equipments:
                    equipment.status = 'Borrowed'
                    equipment.save()
                return super().update(validated_data)
            # If the transaction changes from Borrowed to Finalized and there are no breakages, label the selected equipment's statuses as Working again from Borrowed
            if instance.status == 'Borrowed' and validated_data['transaction_status'] == 'Finalized':
                equipments = validated_data.get('equipments', [])
                for equipment in equipments:
                    equipment.status = 'Working'
                    equipment.save()
                return super().update(validated_data)
            # If the transaction changes from Borrowed to With Breakages, we create a Breakage Report instance
            if instance.status == 'Borrowed' and validated_data['transaction_status'] == 'Finalized':
                BreakageReport.objects.create(
                    transaction=instance,
                    equipments=instance.equipments.all(),
                    resolved=False
                )
            # Changing equipment status of broken items when there are breakages is handled in breakage reports

        return super().update(instance, validated_data)
