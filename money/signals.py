from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from money.models import MoneyItem, Money, AutoPay
from django.utils import timezone


@receiver(post_save, sender=MoneyItem)
def creat_employee(sender, instance, created, **kwargs):
    if created:
        if instance.money.is_income:
            instance.wallet.balance += instance.amount
            instance.wallet.save()
            print('created1')
        else:
            instance.wallet.balance -= instance.amount
            instance.wallet.save()
            print('created2')


# @receiver(post_save, sender=AutoPay)
# def creat_autopay(sender, instance, created, **kwargs):
#     if created:
#         MoneyItem.objects.create(
#             wallet=instance.wallet,
#             money=instance.money,
#             amount=instance.paid_amount,
#             description=instance.description,
#         )
#
#     if not created:
#         MoneyItem.objects.create(
#             wallet=instance.wallet,
#             money=instance.money,
#             amount=instance.paid_amount,
#             description=instance.description,
#         )
