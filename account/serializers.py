from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Wallet, CategoryWallet, ExitSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        User.objects.filter(username=attrs['username'])

        if not user:
            raise serializers.ValidationError('Incorrect username or password.')

        if not user.is_active:
            raise serializers.ValidationError('User is disabled.')

        return {'user': user}


class RegisterationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CategoryWalletSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'description')
        model = CategoryWallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Wallet


class ResetSerializer(serializers.Serializer):
    gmail = serializers.EmailField()


class UserSerializerNew(serializers.Serializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(allow_blank=True, allow_null=True)
    last_name = serializers.CharField(allow_blank=True, allow_null=True)
    email = serializers.EmailField(allow_blank=True, allow_null=True)
    password = serializers.CharField(required=True)


class DeleteUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class WalletExchangeMoneySerializer(serializers.Serializer):
    wallet_id_from = serializers.IntegerField(required=True)
    wallet_id_to = serializers.IntegerField(required=True)
    amount = serializers.FloatField(required=True)
    rate = serializers.FloatField(required=True)

    def validate(self, data):
        if data['wallet_id_from'] == data['wallet_id_to']:
            raise serializers.ValidationError('Wallets must be different.')
        wallet_from = Wallet.objects.get(id=data['wallet_id_from'])
        wallet_to = Wallet.objects.get(id=data['wallet_id_to'])
        if wallet_from.balance < data['amount']:
            raise serializers.ValidationError('Insufficient funds.')
        return data


class ExitSessionSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    exit_time = serializers.IntegerField(required=True)
