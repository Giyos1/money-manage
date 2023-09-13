from django.utils import timezone
from rest_framework import serializers
from .models import Money, MoneyItem, AutoPay, Debt
from account.serializers import WalletSerializer
from account.models import Wallet


class MoneySerializer(serializers.ModelSerializer):
    actually = serializers.SerializerMethodField(read_only=True)

    def get_actually(self, obj):
        return obj.actually()

    class Meta:
        model = Money
        fields = '__all__'


class MoneyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyItem
        fields = '__all__'

    # def validated_data(self):
    #     data = super().validated_data()
    #     if data['wallet'].currency != data['money'].currency:
    #         serializers.ValidationError('Wallet and money must be the same currency.')
    #     return data

    def validate(self, data):
        if data['wallet'].currency != data['money'].currency:
            raise serializers.ValidationError('Wallet and money must be the same currency.')

        return data


class MoneyItemListSerializer(serializers.ModelSerializer):
    money = MoneySerializer(read_only=True)
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = MoneyItem
        fields = '__all__'


class AutoPayListSerializer(serializers.ModelSerializer):
    money = MoneySerializer(read_only=True)
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = AutoPay
        fields = '__all__'


class AutoPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoPay
        fields = '__all__'


class DebtSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    money = MoneySerializer(read_only=True)
    description = serializers.CharField(max_length=255)
    amount = serializers.FloatField()
    paid_amount = serializers.FloatField(default=0)
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    deadline = serializers.DateTimeField()
    is_income = serializers.BooleanField(write_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        if data['paid_amount'] > data['amount']:
            raise serializers.ValidationError('Paid amount must be less than amount.')
        return data
