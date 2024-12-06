from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView
from account.models import *
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import *
from django.core.mail import send_mail


class ShopView(ListView):
    template_name='shop.html'
    queryset=Productss.objects.all()
    context_object_name='products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_products = Productss.objects.all().order_by('-created_at')[:8]
        context['latest_products'] = latest_products

        for product in context['latest_products']:
            avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = avg_rating if avg_rating is not None else 0
    
        for product in context['products']:
            avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = avg_rating if avg_rating is not None else 0
        
        return context
    

class ProductListView(ListView):
    model = Productss
    template_name = 'productlist.html'
    context_object_name = 'products'

    def get_queryset(self):
        cat = self.kwargs.get('cat')
        self.request.session['category'] = cat
        return Productss.objects.filter(category=cat)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get('cat')
        context['category'] = category

        for product in context['products']:
            avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = avg_rating if avg_rating is not None else 0
        return context


class ProductDetailView(DetailView):
    template_name = 'productdetail.html'
    queryset = Productss.objects.all()
    context_object_name = 'product'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        reviews = product.reviews.all()

        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

        context['reviews'] = reviews
        context['avg_rating'] = avg_rating if avg_rating else 0 

        related_products = Productss.objects.filter(category=product.category).exclude(id=product.id)[:4]
        
        for related_product in related_products:
            related_reviews = related_product.reviews.all()
            related_avg_rating = related_reviews.aggregate(Avg('rating'))['rating__avg']
            related_product.avg_rating = related_avg_rating if related_avg_rating else 0 

        context['related_products'] = related_products

        return context


def product_detail(request, id):
    product = get_object_or_404(Productss, pk=id)
    
    avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
    
    form = ProductReviewForm() 
    
    return render(request, 'productdetail.html', {
        'product': product,
        'avg_rating': avg_rating,
        'form': form,
        'category': product.category, 
    })

    
def view_reviews(request, pk):
    product = get_object_or_404(Productss, pk=pk)
    reviews = ProductReview.objects.filter(product=product)
    return render(request, 'view_reviews.html', {
        'product': product,
        'reviews': reviews
    })

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
    review = ProductReview.objects.get(id=review_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        
        if form.is_valid():
            form.save()
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
        
        subtotal = sum(cart.total for cart in carts)
        shipping_fee = sum(
            (int(cart.product.ShippingFee) if cart.product.ShippingFee.isdigit() else 0) * cart.quantity
            for cart in carts
        )
        
        context['subtotal'] = subtotal
        context['shipping_fee'] = shipping_fee
        context['grand_total'] = subtotal + shipping_fee
        return context



def IncreaseQuantity(request, *args, **kwargs):
    try:
        cid = kwargs.get('id')
        cart = Cart.objects.get(id=cid)
        cart.quantity += 1
        cart.save()
        return redirect('cartlist')
    except:
        return redirect('cartlist')

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


def deleteCartItem(request, **kwargs):
    try:
        cid = kwargs.get('id')
        cart = Cart.objects.get(id=cid)
        cart.delete()
        return redirect('cartlist')
    except:
        return redirect('cartlist')
    
@login_required
def add_to_wishlist(request, product_id):
    product = Productss.objects.get(id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    # return redirect('wishlist_view')
    return redirect('shop')


@login_required
def remove_from_wishlist(request, product_id):
    product = Productss.objects.get(id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist_view')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


def placeorder(request, **kwargs):
    try:
        cid = kwargs.get('id')
        if not cid:
            return redirect('cartlist')
        cart = get_object_or_404(Cart, id=cid)
        Orders.objects.create(product=cart.product, user=request.user, quantity=cart.quantity)
        cart.delete()


        # Email sending
        subject = 'Craft.io Order Notification'
        msg = f'Order for {cart.product.title} is placed!!'
        from_email = 'tcsahla@gmail.com'
        to_email = [request.user.email]
        send_mail(subject, msg, from_email, to_email, fail_silently=True)

        return redirect('cartlist')
    except Exception as e:
        return redirect('cartlist')


class OrderListView(ListView):
    template_name = 'orderlist.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Orders.objects.filter(user=self.request.user)


def CancelOrder(request, **kwargs):
    try:
        oid = kwargs.get('id')
        if not oid:
            return redirect('orderlist')
        order = get_object_or_404(Orders, id=oid)
        order.status = 'cancelled'
        order.save()

# Email sending
        subject = 'Craft.io Order Notification'
        msg = f'Order for {order.product.title} is canceled!!'
        from_email = 'tcsahla@gmail.com'
        to_email = [request.user.email]
        send_mail(subject, msg, from_email, to_email, fail_silently=True)

        return redirect('orderlist')
    except Exception as e:
        return redirect('orderlist')