from .models import FinancialRecords, UserProfile
from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['uuid', 'user_name', 'email', 'role', 'is_active']
        read_only_fields = ['uuid']



class FinancialRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecords
        fields = ['uuid', 'created_by', 'amount', 'type_of_record', 'category', 'date', 'notes', 'is_deleted']
        