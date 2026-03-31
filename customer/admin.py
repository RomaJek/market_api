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
    list_display = ('user', )


