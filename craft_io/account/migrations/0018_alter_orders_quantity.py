# Generated by Django 5.1.3 on 2024-12-06 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_orders_total_alter_orders_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='quantity',
            field=models.IntegerField(),
        ),
    ]