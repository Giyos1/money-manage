# Generated by Django 4.2.3 on 2023-09-11 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_alter_exitsession_exit_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exitsession',
            name='exit_time',
            field=models.IntegerField(default=1694173924),
        ),
    ]
