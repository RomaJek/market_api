from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductsView.as_view(), name='warehouse-products'),
    path('productsID/<int:pk>/', views.ProductIDView.as_view(), name='warehouse-products-id'),
    path('category_search/', views.CategorySearchView.as_view(), name='warehouse-category-search'),
    path('category_list/', views.CategoryListView.as_view(), name='warehouse-category-list'),
    
]