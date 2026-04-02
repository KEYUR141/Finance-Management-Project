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


    def validate(self, data):
        try:
            if data is not None:
                if data.get('amount') is not None and data['amount'] < 0:
                    raise serializers.ValidationError("Amount must be non-negative.")
                if data.get('type_of_record') not in ['income', 'expense']:
                    raise serializers.ValidationError("Type of record must be 'income' or 'expense'.")
                if data.get('category') not in ['salary', 'food', 'rent', 'investment', 'other']:
                    raise serializers.ValidationError("Invalid category.")
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))
    
    def create(self, validated_data):
        try:
            if validated_data is not None:
                if validated_data.get('created_by') is None:
                    raise serializers.ValidationError("created_by field is required.")
                if validated_data.get('amount') is None:
                    raise serializers.ValidationError("amount field is required.")
                if validated_data.get('type_of_record') is None:
                    raise serializers.ValidationError("type_of_record field is required.")
                if validated_data.get('category') is None:
                    raise serializers.ValidationError("category field is required.")
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def update(self, instance, validated_data):
        try:
            if validated_data is not None:
                if validated_data.get('amount') is not None and validated_data['amount'] < 0:
                    raise serializers.ValidationError("Amount must be non-negative.")
                if validated_data.get('type_of_record') is not None and validated_data['type_of_record'] not in ['income', 'expense']:
                    raise serializers.ValidationError("Type of record must be 'income' or 'expense'.")
                if validated_data.get('category') is not None and validated_data['category'] not in ['salary', 'food', 'rent', 'investment', 'other']:
                    raise serializers.ValidationError("Invalid category.")
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
    
        