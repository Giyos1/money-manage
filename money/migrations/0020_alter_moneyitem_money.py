# Generated by Django 4.2.3 on 2023-08-21 06:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('money', '0019_alter_autopay_money'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moneyitem',
            name='money',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='money_item', to='money.money'),
        ),
    ]