
# Register your models here.

from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Review
from accounts.models import User

# admin.site.register(Cart)
# admin.site.register(CartItem)
# admin.site.register(Order)
# admin.site.register(OrderItem)
# admin.site.register(Review)


class RoleBasedAdmin(admin.ModelAdmin):
    
    # admin panelde modeldi korsetiwge ruxsat
    def has_module_permission(self, request):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True
        return super().has_module_permission(request)

    # listin koriwge ruxsat
    def has_view_permission(self, request, obj=None):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True
        return super().has_view_permission(request, obj)


@admin.register(Cart)
class CartAdmin(RoleBasedAdmin):

    list_display = ('id', 'user_id', 'user')


@admin.register(CartItem)
class CartItemAdmin(RoleBasedAdmin):

    list_display = ('id', 'cart_id', 'cart__user_id', 'product_id', 'product', 'quantity', 'created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(RoleBasedAdmin):

    list_display = ('id', 'user__id', 'total_price', 'status', 'address')
    search_fields = ('id',)


@admin.register(OrderItem)
class OrderItemAdmin(RoleBasedAdmin):
    list_display = ('id', 'order_id', 'order__user_id', 'product_id', 'quantity', 'price')


@admin.register(Review)
class ReviewAdmin(RoleBasedAdmin):
    list_display = ('id', 'user_id', 'product_id', 'rating', 'text')