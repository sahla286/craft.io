from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView
from account.models import Productss,Cart,ProductReview
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import *


class ShopView(ListView):
    template_name='shop.html'
    queryset=Productss.objects.all()
    context_object_name='products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the latest products (new collections) to the context
        latest_products = Productss.objects.all().order_by('-created_at')[:8]
        context['latest_products'] = latest_products
        return context
    
class ProductListView(ListView):
    template_name = 'productlist.html'
    queryset = Productss.objects.all()
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
    
    

class ProductDetailView(DetailView):
    template_name='productdetail.html'
    queryset=Productss.objects.all()
    context_object_name='product'
    pk_url_kwarg='id' 



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Fetch all reviews related to this product
        reviews = product.reviews.all()
        
        # Calculate the average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Add reviews and average rating to context
        context['reviews'] = reviews
        context['avg_rating'] = avg_rating or 0  # Default to 0 if no reviews
        return context


@login_required
def add_review(request, id):
    product = get_object_or_404(Productss, id=id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('pdetail', id=product.id)
    else:
        form = ProductReviewForm()
    return render(request, 'add_review.html', {'form': form, 'product': product})

@login_required
def update_review(request, review_id):
    # Assuming 'review_id' is passed to get the review object
    review = ProductReview.objects.get(id=review_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        
        if form.is_valid():
            form.save()
            # After saving the form, redirect to the 'add_review' URL
            return redirect(reverse('pdetail', kwargs={'id': review.product.id}))
    else:
        form = ProductReviewForm(instance=review)

    return render(request, 'add_review.html', {'form': form, 'review': review})



@login_required
def delete_review(request, id):
    review = get_object_or_404(ProductReview, id=id, user=request.user)
    product_id = review.product.id
    if request.method == 'POST':
        review.delete()
        return redirect('pdetail', id=product_id)
    return render(request, 'add_review.html', {'review': review})


def addToCart(request,*args,**kwargs):
    try:
        pid=kwargs.get('id')
        product=Productss.objects.get(id=pid)
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
    
