# Generated by Django 5.1.3 on 2024-12-01 13:44

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_remove_products_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
