# Generated by Django 4.2.3 on 2023-09-06 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_remove_token_is_delete_token_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.FloatField(),
        ),
    ]