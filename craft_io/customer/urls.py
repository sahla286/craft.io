# from django.urls import path
# from .views import *

# urlpatterns=[
#     path('products/<str:cat>',ProductListView.as_view(),name='products'),
#     path('pdetail/<int:id>',ProductDetailView.as_view(),name='pdetail'),
#     path('addtocart/<int:id>',addToCart,name='addtocart'),
#     path('cartlist',CartListView.as_view(),name='cartlist'),
#     path('inc/<int:id>',IncreaseQuantity,name='incQuantity'),
#     path('decc/<int:id>',decreaseQuantity,name='decQuantity'),
#     path('removeitem/<int:id>',deleteCartItem,name='removeitem'),
#     path('product/<int:id>/review/', add_review, name='add_review'),
#     path('review/<int:review_id>/update/', update_review, name='update_review'),
#     path('product/<int:pk>/reviews/', view_reviews, name='view_reviews'),

#     # path('review/<int:revid>/update/', update_review, name='update_review'),
#     path('review/<int:id>/delete/',delete_review, name='delete_review'),
# ]



from django.urls import path
from .views import *

urlpatterns = [
    # Make sure that the URL pattern captures the 'cat' argument from the URL
    path('products/<str:cat>/', ProductListView.as_view(), name='products'),

    path('pdetail/<int:id>/', ProductDetailView.as_view(), name='pdetail'),
    path('addtocart/<int:id>/', addToCart, name='addtocart'),
    path('cartlist/', CartListView.as_view(), name='cartlist'),
    path('inc/<int:id>/', IncreaseQuantity, name='incQuantity'),
    path('decc/<int:id>/', decreaseQuantity, name='decQuantity'),
    path('removeitem/<int:id>/', deleteCartItem, name='removeitem'),
    path('product/<int:id>/review/', add_review, name='add_review'),
    path('review/<int:review_id>/update/', update_review, name='update_review'),
    path('product/<int:pk>/reviews/', view_reviews, name='view_reviews'),
    path('review/<int:id>/delete/', delete_review, name='delete_review'),
    path('add-to-wishlist/<int:product_id>/',add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/',remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/',wishlist_view, name='wishlist_view'),
    path('placeorder/<int:id>', placeorder, name='placeorder'),
    path('orderlist', OrderListView.as_view(), name='orderlist'),
    path('corder/<int:id>', CancelOrder, name='corder'),
]
