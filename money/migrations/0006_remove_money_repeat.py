# Generated by Django 4.2.3 on 2023-07-11 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0005_moneyitem_transaction_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='money',
            name='repeat',
        ),
    ]
