# Generated by Django 4.2.3 on 2023-08-23 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0023_alter_autopay_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='money',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
