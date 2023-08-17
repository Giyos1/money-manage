# Generated by Django 4.2.3 on 2023-08-15 09:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_wallet_active'),
        ('money', '0014_alter_money_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoPay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=1000)),
                ('amount', models.IntegerField()),
                ('deadline', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paid_amount', models.IntegerField(default=0)),
                ('money', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='money.money')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.wallet')),
            ],
        ),
    ]
