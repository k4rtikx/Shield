from rest_framework import serializers

class FraudAnalysisSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()