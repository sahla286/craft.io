# Generated by Django 5.1.3 on 2024-12-08 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0022_remove_deliveryaddress_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]