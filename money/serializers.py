from rest_framework import serializers
from .models import Money, MoneyItem
from account.serializers import WalletSerializer


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
