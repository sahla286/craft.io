from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView
from account.models import *
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import *
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html


def signin_required(fn):
    def inner(request, *args, **kw):
        if request.user.is_authenticated:
            return fn(request, *args, **kw)
        else:
            messages.error(request, 'Please login First!!')
            return redirect('login')
    return inner

decorators = [signin_required, never_cache]


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
        
        sort_option = self.request.GET.get('sortby')
        queryset = Productss.objects.filter(category=cat)
        if sort_option == 'price_asc':
            queryset = queryset.order_by('offerprice')
        elif sort_option == 'price_desc':
            queryset = queryset.order_by('-offerprice')
        elif sort_option == 'newest':
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get('cat')
        context['category'] = category
        for product in context['products']:
            avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = avg_rating if avg_rating is not None else 0
        context['sortby'] = self.request.GET.get('sortby', '')
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

@signin_required
def view_reviews(request, pk):
    product = get_object_or_404(Productss, pk=pk)
    reviews = ProductReview.objects.filter(product=product)
    return render(request, 'view_reviews.html', {
        'product': product,
        'reviews': reviews
    })

@signin_required
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
    review = get_object_or_404(ProductReview, id=review_id)

    # Ensure the product's category exists before rendering the template
    if not review.product.category:
        # Redirect to a fallback page if the category is missing
        return redirect('shop')

    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        
        if form.is_valid():
            form.save()
            return redirect(reverse('pdetail', kwargs={'id': review.product.id}))
    else:
        form = ProductReviewForm(instance=review)

    return render(request, 'add_review.html', {'form': form, 'review': review})


@signin_required
def delete_review(request, id):
    review = get_object_or_404(ProductReview, id=id, user=request.user)
    product_id = review.product.id
    if request.method == 'POST':
        review.delete()
        return redirect('pdetail', id=product_id)
    return render(request, 'add_review.html', {'review': review})

@signin_required
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
    
@method_decorator(decorator=decorators, name='dispatch')
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
    
@signin_required
def add_to_wishlist(request, product_id):
    product = Productss.objects.get(id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    # return redirect('wishlist_view')
    return redirect('shop')



def remove_from_wishlist(request, product_id):
    product = Productss.objects.get(id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist_view')


@signin_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@signin_required
def placeorder(request):
    try:
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cartlist')
        for cart in cart_items:
            Orders.objects.create(
                product=cart.product,
                user=request.user,
                quantity=cart.quantity,
                total=cart.total,
            )
            cart.delete()
            subject = 'Craft.io Order Confirmation'
            html_content = format_html(
                f"""
                <p>Hi <strong>{request.user.username}</strong>,</p>
                <p>Your order has been successfully placed.</p>
                <p>
                   
                    <strong>Product:</strong> {cart.product.title} <br>
                    <strong>Quantity:</strong> {cart.quantity} <br>
                    <strong>Total Price:</strong> ₹{cart.total}
                </p>
                <p>Thank you for shopping with us!</p>
                """
            )
            email = EmailMultiAlternatives(subject, '', to=[request.user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()

        messages.success(request, 'Your order has been successfully placed! Thank you for shopping with us!')
        return redirect('orderlist')

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('cartlist')

@method_decorator(decorator=decorators, name='dispatch')
class OrderListView(ListView):
    template_name = 'orderlist.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Orders.objects.filter(user=self.request.user)

@signin_required
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



# Search Product
def searchproduct(request):
    keyword = request.POST.get('searchkey', '')
    cat = request.session.get('category', '')
    if keyword:
        products = Productss.objects.filter(title__icontains=keyword, category=cat)
        return render(request, 'productlist.html', {'products': products})
    else:
        return redirect('products', cat=cat)
    
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        full_message = f"Message from {name} ({email}):\n\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                'tcsahla@gmail.com',  # Replace with your email
                [request.user.email],  # Replace with the recipient's email
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('contact')  # Redirect to the same page after submission

    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')



@login_required
def add_delivery_address(request):
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('placeorder') 
    else:
        form = DeliveryAddressForm()

    return render(request, 'delivery_address_form.html', {'form': form})


# @login_required
# def edit_delivery_address(request, address_id):
#     address = DeliveryAddress.objects.get(id=address_id, user=request.user)
    
#     if request.method == 'POST':
#         form = DeliveryAddressForm(request.POST, instance=address)
#         if form.is_valid():
#             form.save()
#             return redirect('placeorder')

#     else:
#         form = DeliveryAddressForm(instance=address)

#     return render(request, 'delivery_address_form.html', {'form': form})


# @login_required
# def order_summary(request):
#     # Check if the user has a delivery address
#     address = DeliveryAddress.objects.filter(user=request.user).first()
#     if not address:
#         return redirect('add_delivery_address')  # Redirect to the add address page if no address exists

#     # If the address exists, render the order summary
#     return render(request, 'order_summary.html', {'address': address})



