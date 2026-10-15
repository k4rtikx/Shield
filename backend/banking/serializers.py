from rest_framework import serializers


class BankAccountSerializer(serializers.Serializer):
    account_holder = serializers.CharField(max_length=150)
    account_type = serializers.ChoiceField(
        choices=["savings", "current"]
    )
    initial_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0
    )