import json
from datetime import datetime

from account.serializers import WalletSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from .models import Money, MoneyItem
from .serializers import MoneySerializer, MoneyItemSerializer, MoneyItemListSerializer
from .utils import summ_usd, summ_uzs, usd_to_uzd, uzd_to_usd
from account.models import Wallet


class MoneyViewSet(ModelViewSet):
    queryset = Money.objects.all()
    serializer_class = MoneySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
        queryset_income = queryset.filter(money__is_income=True, created_at__month=time.month)
        queryset_outcome = queryset.filter(money__is_income=False, created_at__month=time.month)
        income_uzs = summ_uzs(queryset_income)
        income_usd = summ_usd(queryset_income)
        outcome_uzs = summ_uzs(queryset_outcome)
        outcome_usd = summ_usd(queryset_outcome)
        balance_uzs = income_uzs - outcome_uzs
        balance_usd = income_usd - outcome_usd
        user_wallets = Wallet.objects.filter(user=self.request.user, active=True)
        data = WalletSerializer(user_wallets, many=True).data
        # print(json.dumps(data, indent=4, sort_keys=True))
        total_balance_wallets = 0
        for wallet in user_wallets:
            if wallet.currency == 'UZS':
                # print(wallet.balance)
                total_balance_wallets += wallet.balance
                # print(total_balance_wallets)

            elif wallet.currency == 'USD':
                # print(wallet.balance)
                total_balance_wallets += usd_to_uzd(wallet.balance)
                # print('dollar=',usd_to_uzd(wallet.balance))
                # print(total_balance_wallets)

        total_balance_uzs = balance_uzs + total_balance_wallets
        total_balance_usd = balance_usd + uzd_to_usd(total_balance_wallets)

        return Response(data={'income_uzs': income_uzs, 'income_usd': income_usd, 'outcome_uzs': outcome_uzs,
                              'outcome_usd': outcome_usd, 'total_balance_uzs': total_balance_uzs,
                              'total_balance_usd': total_balance_usd})
