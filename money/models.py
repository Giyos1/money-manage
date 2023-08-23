from django.db import models
from django.utils import timezone
import requests

x = requests.get('https://cbu.uz/ru/arkhiv-kursov-valyut/json/')
sum_rate = x.json()[0]['Rate']


# class CategoryMoney(models.Model):
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name


class Money(models.Model):
    choice_currency = (
        ('USD', 'usd'),
        ('UZS', 'uzs'),
        ('RUB', 'rub'),
        ('EUR', 'eur'),
    )
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    is_income = models.BooleanField(default=False)
    target_money = models.IntegerField()
    currency = models.CharField(max_length=100, choices=choice_currency)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def actually(self):
        # items = []
        # for item in self.money_item.all():
        #     if item.wallet.currency == self.currency:
        #         items.append(item)
        #     else:
        #         if item.wallet.currency == 'USD':
        #             items.append(item.amount * sum_rate)
        #         elif item.wallet.currency == 'UZS':
        #             items.append(item.amount
        return sum([item.amount for item in self.money_item.all()])

    def __str__(self):
        return '{} '.format(self.name)

    class Meta:
        ordering = ['-created_at']


class MoneyItem(models.Model):
    money = models.ForeignKey(Money, on_delete=models.SET_NULL, related_name='money_item', null=True, blank=True)
    description = models.TextField(max_length=1000)
    amount = models.IntegerField()
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wallet = models.ForeignKey('account.Wallet', on_delete=models.CASCADE)

    # def __str__(self):
    #     return '{} - {}'.format(self.money.name, self.amount)

    class Meta:
        ordering = ['-created_at']


class RepeatMoney(models.Model):
    choice_repeat = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('no repeat', 'No Repeat'),
    )
    balance = models.IntegerField()
    repeat = models.CharField(max_length=100, choices=choice_repeat)
    target_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AutoPay(models.Model):
    money = models.ForeignKey(Money, on_delete=models.CASCADE, related_name='auto_pay')
    description = models.TextField(max_length=1000)
    amount = models.IntegerField(default=0)
    deadline = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_amount = models.IntegerField(default=0)
    wallet = models.ForeignKey('account.Wallet', on_delete=models.CASCADE)
