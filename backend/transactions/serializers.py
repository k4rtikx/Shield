from rest_framework import serializers

class MoneyTransferSerializer(serializers.Serializer):
    sender_account_id = serializers.CharField()
    receiver_account_id = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01
    )