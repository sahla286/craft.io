# Generated by Django 5.1.3 on 2024-12-06 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_alter_orders_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='total',
            field=models.IntegerField(),
        ),
    ]