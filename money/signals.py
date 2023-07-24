from django.dispatch import receiver
from django.db.models.signals import post_save
from money.models import MoneyItem, Money


@receiver(post_save, sender=MoneyItem)
def creat_employee(sender, instance, created, **kwargs):
    if created:
        if instance.money.is_income:
            instance.wallet.balance += instance.amount
            instance.wallet.save()
        else:
            instance.wallet.balance -= instance.amount
            instance.wallet.save()
