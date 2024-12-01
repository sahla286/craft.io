from django.urls import path
from .views import *

urlpatterns=[
    path('products/<str:cat>',ProductListView.as_view(),name='products'),
    path('pdetail/<int:id>',ProductDetailView.as_view(),name='pdetail'),
    path('addtocart/<int:id>',addToCart,name='addtocart'),
    path('cartlist',CartListView.as_view(),name='cartlist'),
    path('inc/<int:id>',IncreaseQuantity,name='incQuantity'),
    path('decc/<int:id>',decreaseQuantity,name='decQuantity'),
    path('removeitem/<int:id>',deleteCartItem,name='removeitem'),
]