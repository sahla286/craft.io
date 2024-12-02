from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# Create your models here.

class Productss(models.Model):
    title=models.CharField(max_length=100)
    description=models.CharField(max_length=500)
    price=models.IntegerField()
    offerprice=models.IntegerField()
    image=models.ImageField(upload_to='product_images')
    stock=models.IntegerField()
    ShippingFee=models.CharField(max_length=100,default='Free')
    created_at = models.DateTimeField(default=timezone.now)
    options=(
        ('PaperCraft','PaperCraft'),
        ('Wooden','Wooden'),
        ('Jute','Jute'),
    )
    category=models.CharField(max_length=100,choices=options)
    def __str__(self) -> str:
        return self.title
    
class Cart(models.Model):
    product=models.ForeignKey(Productss,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    total=models.IntegerField()

    def save(self, *args, **kwargs):
        # Calculate the total price for the cart item before saving
        self.total = self.product.price * self.quantity
        super().save(*args, **kwargs)