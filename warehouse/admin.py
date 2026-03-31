
from django.contrib import admin
import re

from .models import Category, Product
from accounts.models import User


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

    def has_change_permission(self, request, obj=None):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True
        return super().has_add_permission(request)
        
    def has_delete_permission(self, request, obj=None):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True 
        return super().has_delete_permission(request, obj)



@admin.register(Category)
class CategoryAdmin(RoleBasedAdmin):


    list_display = ('name', 'slug', 'parent', 'id')
    list_filter = ('parent', )
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ['name', ]
    autocomplete_fields = ('parent', )



@admin.register(Product)
class ProductAdmin(RoleBasedAdmin):

    list_display = ('name', 'stock', 'price', 'discount_price', 'category', 'is_active', 'id')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'slug', 'stock')
    prepopulated_fields = {'slug': ('name', )}  # slug avtomat jaziliwi ushin
    autocomplete_fields = ('category', )    # dropdown ishinde search qiliwga boladi categorylar ko'beyip ketkende izlep ansat boladi



    
