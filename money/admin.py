from django.contrib import admin
from money.models import MoneyItem, Money, RepeatMoney, AutoPay


@admin.register(MoneyItem)
class MoneyItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'money', 'amount', 'description', 'transaction_date')



admin.site.register(Money)
admin.site.register(RepeatMoney)
admin.site.register(AutoPay)
