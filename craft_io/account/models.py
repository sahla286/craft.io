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


class ProductReview(models.Model):
    product = models.ForeignKey(Productss, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)  # Ratings from 1 to 5
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} - {self.rating}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Productss, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"
    

class Orders(models.Model):
    product = models.ForeignKey(Productss, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datatime = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()  # Change this to IntegerField
    total = models.IntegerField() 
    
    options = (
        ('OrderPlaced', 'OrderPlaced'),
        ('Shipped', 'Shipped'),
        ('OutForDelivery', 'OutForDelivery'),
        ('Delivered', 'Delivered'),
        ('cancelled', 'cancelled')
    )
    status = models.CharField(max_length=100, default='OrderPlaced', choices=options)

    def __str__(self) -> str:
        return f"Order by {self.user.username} for {self.product} on {self.datatime.strftime('%Y-%m-%d %H:%M:%S')}"
