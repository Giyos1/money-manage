# Generated by Django 4.2.3 on 2023-08-21 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0021_alter_moneyitem_money'),
    ]

    operations = [
        migrations.AddField(
            model_name='money',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]