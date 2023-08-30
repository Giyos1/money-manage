import requests
from money.models import MoneyItem
def sum_rate():
    x = requests.get('https://cbu.uz/ru/arkhiv-kursov-valyut/json/')
    return x.json()[0]['Rate']


def uzd_to_usd(value):
    return int(value) / float(sum_rate())


def usd_to_uzd(value):
    return int(value) * float(sum_rate())


def summ_usd(queryset):
    usd_query = queryset.filter(wallet__currency='USD')
    uzs_query = queryset.filter(wallet__currency='UZS')
    usd_sum = 0
    for item in usd_query:
        usd_sum += item.amount
    uzs_sum = 0
    for item in uzs_query:
        uzs_sum += uzd_to_usd(item.amount)
    return usd_sum + uzs_sum


def summ_uzs(queryset):
    usd_query = queryset.filter(wallet__currency='USD')
    uzs_query = queryset.filter(wallet__currency='UZS')
    usd_sum = 0
    for item in usd_query:
        usd_sum += usd_to_uzd(item.amount)
    uzs_sum = 0
    for item in uzs_query:
        uzs_sum += item.amount
    return usd_sum + uzs_sum
