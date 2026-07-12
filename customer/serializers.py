from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Review

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['cart',]    # cart ID request arqali jibere almawi ushin, ozimiz aniqlaymiz

    def validate(self, attrs):
        # jiberilgen pruduct ham quantity alamiz
        product = attrs.get('product')

        # Eger quantity jiberilmese defualt 1 dep alamiz, Modelde bugan ruxsat bar
        quantity = attrs.get('quantity', 1)

        if product.stock == 0:
            raise serializers.ValidationError({
                "product": "Bul product bazada tawsilgen, qalmagan"
            })
        elif not product.is_active:
            raise serializers.ValidationError({
                "is_active": "Bul product active emes"
            })
        return attrs


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'text', 'rating']
        read_only_fields = ['id', 'user'] # user request'dan olinadi













class OrderCreateSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=512, required=True)
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True, # Majburiy
        help_text="Satip alinatugin CartItem ID lar listi (Misali: [1, 2, 5])"
    )


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True) # Nested serializer 

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'address', 'orderitems', 'created_at']



