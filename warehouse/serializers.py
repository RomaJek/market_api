# serializer ishinde discount_price < price boliwin tekseriw kerek

from rest_framework import serializers
from decimal import Decimal

from .models import Category, Product



class CategorySearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=10, max_value=100, default=10, required=False)

class CategoryListSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1, required=False)
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=10, max_value=100, default=10, required=False)
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        exclude = ['is_active',]    # is_activedan basqa hammesin shigar






class ProductCreateSerializer(serializers.ModelSerializer):

    # image = serializers.ImageField(required=False)

    class Meta:
        model  = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'discount_price',
            'stock',
            'is_active',
            'image'
        ]
        # slug avtomatik jaratilgani ushin oni read_only qildim
        # Swaggerde oni kiritiwdi soramaymiz
        read_only_fields = ['slug',] 

 
    def validate(self, attrs):
        price = attrs.get('price')
        discount_price = attrs.get('discount_price')
 
        # eger ekewide kirilgen ham discount_price 0 den ulken bolsa
        if price is not None and discount_price is not None:
            if discount_price > 0 and discount_price >= price:
                raise serializers.ValidationError(
                    {'discount_price': "Shegirme (discount_price) negizgi (price) bahasinan kishi boliwi kerek."}
                )
        return attrs
 

 
class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Productti update qiliw ushin. PATCH - kerekli fieldlardi saylap ozgertiw
    """
    class Meta:
        model  = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'discount_price',
            'stock',
            'is_active',
            'image'
        ]
        read_only_fields = ['slug',]
 
    def validate(self, attrs):
        # PATCHda requestda jiberilgen fieldlardi, eger jiberilmese bazadagi (instance) sanlardi alamiz.
        # attrs.get - requist-dan aladi, eger joq bolsa getattr(self.instance, ... ) bazadan barip alip keledi
        price = attrs.get('price', getattr(self.instance, 'price', None))
        discount_price = attrs.get('discount_price', getattr(self.instance, 'discount_price', None))
 
        # discount_price price-dan usken yamasa ten bolip qalmawin tekseredi
        if price is not None and discount_price is not None:
            if discount_price > 0 and discount_price >= price:
                raise serializers.ValidationError(
                    {'discount_price': "Shegirme (discount_price) negizgi (price) bahasinan kishi boliwi kerek."}
                )
        return attrs