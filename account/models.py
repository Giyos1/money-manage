from django.db import models
from django.contrib.auth.models import User


class CategoryWallet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name


class Wallet(models.Model):
    choice_currency = (
        ('USD', 'usd'),
        ('UZS', 'uzs'),
        ('RUB', 'rub'),
        ('EUR', 'eur'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryWallet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.IntegerField()
    currency = models.CharField(max_length=100, choices=choice_currency)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
