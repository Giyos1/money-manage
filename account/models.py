from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    balance = models.FloatField()
    currency = models.CharField(max_length=100, choices=choice_currency)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        if self.balance < 0:
            raise ValidationError('Balance must be positive.')
        super().full_clean(exclude, validate_unique, validate_constraints)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['-created_at']


class Token(models.Model):
    token = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ExitSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    exit_time = models.IntegerField(default=int(timezone.now().timestamp()))
