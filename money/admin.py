from django.contrib import admin
from money.models import MoneyItem, Money, RepeatMoney


admin.site.register(MoneyItem)
admin.site.register(Money)
admin.site.register(RepeatMoney)
