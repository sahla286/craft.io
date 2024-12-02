from django.db import migrations, models
from django.utils import timezone  # Import timezone for the current date and time

class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_products_shippingfee'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),  # Use timezone.now for the default value
            preserve_default=False,
        ),
    ]
