from account.models import Cart,Wishlist,Orders

def item_count(request):
    if request.user.is_authenticated:
        cart_count=Cart.objects.filter(user=request.user).count()
        wishlist_count=Wishlist.objects.filter(user=request.user).count()
        order_count=Orders.objects.filter(user=request.user).count()
        return {'cart':cart_count,'wishlist':wishlist_count,'order':order_count}
    else:
        return {"cart":0,'wishlist':0,"order":0}
    

    # your_app/context_processors.py


# from django.db.models import Avg, Count

# def product_review_data(request):
#     products = ProductReview.objects.all()
    
#     product_review_info = {}
    
#     for product in products:
#         total_reviews = product.reviews.count()  # Get total reviews
#         avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']  # Get average rating
        
#         product_review_info[product.id] = {
#             'total_reviews': total_reviews,
#             'avg_rating': round(avg_rating, 1) if avg_rating else 0  # Return average rating rounded to 1 decimal
#         }

#     return {
#         'product_review_info': product_review_info
#     }
