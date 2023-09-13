import json
from datetime import datetime

from django.db.models import Sum, Q
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework.views import APIView

from account.serializers import WalletSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from .models import Money, MoneyItem, AutoPay, Debt
from .serializers import MoneySerializer, MoneyItemSerializer, MoneyItemListSerializer, AutoPaySerializer, \
    AutoPayListSerializer, DebtSerializer
from .utils import sum_rate, usd_to_uzd, uzd_to_usd
from account.models import Wallet


class MoneyOrderUpdateViewSet(ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data['order']
        for item in data:
            try:
                money = Money.objects.get(id=item['id'])
                money.order = item['order']
                money.save()
            except Money.DoesNotExist:
                pass
        return Response(data={'message': 'Update success'}, status=200)


class MoneyViewSet(ModelViewSet):
    queryset = Money.objects.all()
    serializer_class = MoneySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        money_list = []
        for money in queryset:
            print(money.is_deleted)
            auto_pays = money.auto_pay.all()
            money_list.append({
                'id': money.id,
                'name': money.name,
                'currency': money.currency,
                'is_income': money.is_income,
                'actually': money.actually(),
                'target_money': money.target_money,
                'created_at': money.created_at,
                'updated_at': money.updated_at,
                'order': money.order,
                'auto_pays': AutoPayListSerializer(auto_pays, many=True).data
            })

        return Response(data=money_list)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(data={'message': 'Delete success'}, status=200)


class MoneyItemViewSet(ModelViewSet):
    queryset = MoneyItem.objects.all()
    serializer_class = MoneyItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(wallet__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset_income = queryset.filter(money__is_income=True)
        queryset_outcome = queryset.filter(money__is_income=False)
        dict_income = MoneyItemListSerializer(queryset_income, many=True).data
        dict_outcome = MoneyItemListSerializer(queryset_outcome, many=True).data
        return Response(data={'income': dict_income, 'outcome': dict_outcome})


class StatusViewSet(ViewSet):
    queryset = MoneyItem.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(wallet__user=self.request.user)

    def list(self, request, *args, **kwargs):
        time = datetime.now()
        queryset = self.get_queryset()
        rate = sum_rate()
        aggregated_qs = queryset.filter(created_at__year=time.year, created_at__month=time.month).aggregate(
            income_uzs=Sum('amount', filter=Q(money__is_income=True, wallet__currency='UZS')),
            income_usd=Sum('amount', filter=Q(money__is_income=True, wallet__currency='USD')),
            outcome_uzs=Sum('amount', filter=Q(money__is_income=False, wallet__currency='UZS')),
            outcome_usd=Sum('amount', filter=Q(money__is_income=False, wallet__currency='USD')),
        )
        income_uzs = aggregated_qs['income_uzs'] + aggregated_qs['income_usd'] * float(rate)
        income_usd = aggregated_qs['income_uzs'] / float(rate) + aggregated_qs['income_usd']
        outcome_uzs = aggregated_qs['outcome_uzs'] + aggregated_qs['outcome_usd'] * float(rate)
        outcome_usd = aggregated_qs['outcome_uzs'] / float(rate) + aggregated_qs['outcome_usd']
        user_wallets = Wallet.objects.filter(user=self.request.user, active=True).aggregate(
            total_balance_uzs=Sum('balance', filter=Q(currency='UZS')),
            total_balance_usd=Sum('balance', filter=Q(currency='USD'))
        )
        total_balance_wallets = user_wallets['total_balance_uzs'] + user_wallets['total_balance_usd'] * float(rate)
        total_balance_wallets_usd = user_wallets['total_balance_uzs'] / float(rate) + user_wallets['total_balance_usd']

        return Response(data={'income_uzs': income_uzs, 'income_usd': income_usd, 'outcome_uzs': outcome_uzs,
                              'outcome_usd': outcome_usd, 'total_balance_uzs': total_balance_wallets,
                              'total_balance_usd': total_balance_wallets_usd})


class AutoPayViewSet(ModelViewSet):
    queryset = AutoPay.objects.all()
    serializer_class = AutoPaySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(wallet__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            wallet = data['wallet']
            money = data['money']
            amount = data['amount']
            paid_amount = data['paid_amount']
            deadline = data['deadline']
            description = data['description']
            if paid_amount > 0:
                MoneyItem.objects.create(
                    wallet=wallet,
                    money=money,
                    amount=paid_amount,
                    description=description,
                )
            if amount <= paid_amount:
                deadline = deadline + timezone.timedelta(
                    days=(paid_amount // amount) * 30)
                paid_amount = paid_amount % amount
            a = AutoPay.objects.create(wallet=wallet, money=money, amount=amount, paid_amount=paid_amount,
                                       deadline=deadline, description=description)
            serializer = AutoPaySerializer(a)
        return Response(status=200, data=serializer.data)

    @atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            m1 = None
            data = serializer.validated_data
            wallet = data['wallet']
            money = data['money']
            amount = data['amount']
            paid_amount = data['paid_amount']
            deadline = data['deadline']
            description = data['description']
            if paid_amount != instance.paid_amount:
                m1 = MoneyItem.objects.create(
                    wallet=wallet,
                    money=money,
                    amount=paid_amount - instance.paid_amount,
                    description=description,
                )

            if amount <= paid_amount:
                deadline = deadline + timezone.timedelta(
                    days=(paid_amount // amount) * 30)
                paid_amount = paid_amount % amount
            instance.wallet = wallet
            instance.money = money
            instance.amount = amount
            instance.paid_amount = paid_amount
            instance.deadline = deadline
            instance.description = description
            instance.save()
            serializer_auto_pay = AutoPaySerializer(instance)
            if m1:
                serializer_transaction = MoneyItemSerializer(m1)
                return Response(status=200,
                                data={'auto_pay': serializer_auto_pay.data, 'transaction': serializer_transaction.data})
            return Response(status=200, data={'auto_pay': serializer_auto_pay.data})


class DebtViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

    def get_queryset(self):
        return self.queryset.filter(wallet__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @atomic
    def create(self, request, *args, **kwargs):
        dict1 = {}
        serializer = self.get_serializer(data=request.data)
        money = Money.objects.filter(user=self.request.user, is_debt=True)
        if serializer.is_valid():
            data = serializer.validated_data
            wallet = data['wallet']
            amount = data['amount']
            paid_amount = data['paid_amount']
            deadline = data['deadline']
            description = data['description']
            is_income = data['is_income']
            if not money:
                Money.objects.create(user=self.request.user,
                                     name='Qarz olish',
                                     is_income=True,
                                     target_money=0,
                                     currency='UZS',
                                     is_deleted=True,
                                     is_debt=True)
                Money.objects.create(user=self.request.user,
                                     name='Qarz berish',
                                     is_income=False,
                                     target_money=0,
                                     currency='UZS',
                                     is_deleted=True,
                                     is_debt=True)
                money = Money.objects.filter(user=self.request.user, is_debt=True)

            if is_income:
                d1 = Debt.objects.create(wallet=wallet, money=money.filter(is_income=True).first(), amount=amount,
                                         paid_amount=paid_amount, description=description, deadline=deadline)
            else:
                d1 = Debt.objects.create(wallet=wallet, money=money.filter(is_income=False).first(), amount=amount,
                                         paid_amount=paid_amount, description=description, deadline=deadline)
            m1 = MoneyItem.objects.create(wallet=wallet, money=money.filter(is_income=is_income).first(), amount=amount,
                                          description=description)
            dict1['Debt'] = DebtSerializer(d1).data
            dict1['MoneyItem'] = MoneyItemSerializer(m1).data
            return Response(status=200, data=dict1)
        return Response(status=400, data=serializer.errors)

    @atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            m1 = None
            data = serializer.validated_data
            wallet = data['wallet']
            amount = data['amount']
            paid_amount = data['paid_amount']
            deadline = data['deadline']
            description = data['description']

            money = Money.objects.filter(user=self.request.user, is_debt=True)
            is_income = not (instance.money.is_income)
            money = money.filter(is_income=is_income).first()

            if paid_amount != instance.paid_amount:
                m1 = MoneyItem.objects.create(
                    wallet=wallet,
                    money=money,
                    amount=paid_amount - instance.paid_amount,
                    description=description,
                )
            instance.wallet = wallet
            instance.amount = amount
            instance.paid_amount = paid_amount
            instance.deadline = deadline
            instance.description = description
            if instance.amount == instance.paid_amount:
                instance.is_active = False
            instance.save()
            serializer_debt = DebtSerializer(instance)
            if m1:
                serializer_transaction = MoneyItemSerializer(m1)
                return Response(status=200,
                                data={'debt': serializer_debt.data, 'transaction': serializer_transaction.data})
            return Response(status=200, data={'debt': serializer_debt.data})
