# Generated by Django 4.2.3 on 2023-07-07 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='moneyitem',
            old_name='price',
            new_name='amount',
        ),
        migrations.AlterField(
            model_name='moneyitem',
            name='money',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='money.money'),
        ),
    ]
