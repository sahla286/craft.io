from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView
from account.models import Products,Cart

class ShopView(ListView):
    template_name='shop.html'
    queryset=Products.objects.all()
    context_object_name='products'
    
class ProductListView(ListView):
    template_name = 'productlist.html'
    queryset = Products.objects.all()
    context_object_name = 'products'  # key name for products

    def get_queryset(self):
        cat = self.kwargs.get('cat')
        self.request.session['category'] = cat
        return self.queryset.filter(category=cat)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the category name to the context for banner image logic
        category = self.kwargs.get('cat')
        context['category'] = category
        return context

# def new_collections_view(request):
#     latest_products = Products.objects.all().order_by('-created_at')[:8]
#     return render(request, 'your_template.html', {'latest_products': latest_products})

class ProductDetailView(DetailView):
    template_name='productdetail.html'
    queryset=Products.objects.all()
    context_object_name='product'
    pk_url_kwarg='id' 

def addToCart(request,*args,**kwargs):
    try:
        pid=kwargs.get('id')
        product=Products.objects.get(id=pid)
        user=request.user
        cartcheck=Cart.objects.filter(product=product,user=user).exists()
        if cartcheck:
            cartitem=Cart.objects.get(product=product,user=user)
            cartitem.quantity+=1
            cartitem.save()
            return redirect('cartlist')
        else:
            Cart.objects.create(product=product,user=user)
            return redirect('cartlist')
    except Exception as e:
        print(f"Error in addToCart: {e}")
        return redirect('cartlist')
    
class CartListView(ListView):
    template_name = 'cart.html'
    queryset=Cart.objects.all()
    context_object_name = 'carts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carts = self.get_queryset()
        
        # Calculate subtotal
        subtotal = sum(cart.total for cart in carts)
        
        # Calculate total shipping fee
        shipping_fee = sum(
            (int(cart.product.ShippingFee) if cart.product.ShippingFee.isdigit() else 0) * cart.quantity
            for cart in carts
        )
        
        # Pass calculated values to context
        context['subtotal'] = subtotal
        context['shipping_fee'] = shipping_fee
        context['grand_total'] = subtotal + shipping_fee
        return context


# Increase Quantity
def IncreaseQuantity(request, *args, **kwargs):
    try:
        cid = kwargs.get('id')
        cart = Cart.objects.get(id=cid)
        cart.quantity += 1
        cart.save()
        return redirect('cartlist')
    except:
        return redirect('cartlist')

# Decrease Quantity
def decreaseQuantity(request, *args, **kwargs):
    try:
        cid = kwargs.get('id')
        cart = Cart.objects.get(id=cid)
        if cart.quantity == 1:
            cart.delete()
        else:
            cart.quantity -= 1
            cart.save()
        return redirect('cartlist')
    except:
        return redirect('cartlist')

# Delete Cart Item
def deleteCartItem(request, **kwargs):
    try:
        cid = kwargs.get('id')
        cart = Cart.objects.get(id=cid)
        cart.delete()
        return redirect('cartlist')
    except:
        return redirect('cartlist')
    
