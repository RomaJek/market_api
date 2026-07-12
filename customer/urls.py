from django.urls import path
from . import views

urlpatterns = [
    path('cart_item/', views.CartItemListCreateView.as_view(), name='order-cartitem'),
    path('cart-item/<int:pk>/', views.CartItemDeleteView.as_view(), name='order-cartitem-delete'),
    path('order/checkout/', views.OrderCreateListView.as_view(), name='order-checkout'),
    path('order/<int:pk>/pay/', views.OrderPayView.as_view(), name='order-pay'),
    path('review/', views.ReviewCreateGetView.as_view(), name='review-create-get'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    path('review/<int:pk>/list/product/', views.ReviewListProduct.as_view(), name='review-list-product'),
]