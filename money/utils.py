import requests
from money.models import MoneyItem
def sum_rate():
    x = requests.get('https://cbu.uz/ru/arkhiv-kursov-valyut/json/')
    return x.json()[0]['Rate']


def uzd_to_usd(value):
    return int(value) / float(sum_rate())


def usd_to_uzd(value):
    return int(value) * float(sum_rate())

