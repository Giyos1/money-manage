# Generated by Django 4.2.3 on 2023-09-13 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0029_alter_debt_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt',
            name='paid_amount',
            field=models.FloatField(default=0),
        ),
    ]
