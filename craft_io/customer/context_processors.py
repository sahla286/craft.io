from account.models import Cart,Wishlist

def item_count(request):
    if request.user.is_authenticated:
        cart_count=Cart.objects.filter(user=request.user).count()
        wishlist_count=Wishlist.objects.filter(user=request.user).count()
        return {'cart':cart_count,'wishlist':wishlist_count}
    else:
        return {"cart":0,'wishlist':0}