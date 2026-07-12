# Create your views here.


from django.shortcuts import render
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from django.shortcuts import get_object_or_404


from core.schema import (
    wrapped_response,
    ErrorResponseSerializer,
    MessageResponseSerializer
)
from core.pagination import (
    paginate_queryset,
)
from core.response import error_response, success_response


from .models import (
    Cart,
    CartItem, 
    Order, 
    OrderItem,
    Review,
)
from warehouse.models import Product
from warehouse.serializers import ProductSerializer
from accounts.permissions import IsAuthenticated
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ReviewSerializer,
)


class CartItemListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cart'],
        request=CartItemSerializer,
        responses={
            201: wrapped_response(CartItemSerializer),
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = serializer.validated_data.get('product')
        new_quantity = serializer.validated_data.get('quantity', 1)

        cart, created = Cart.objects.get_or_create(user=request.user)
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        
        if new_quantity > product.stock:
            raise ValidationError({
                "quantity": f"Siz soragan {new_quantity} dana product joq. Bazada {product.stock} dana bar."
            })
        
        """ Save (update yamasa tazadan jaratiw)"""
        if existing_item:
            """ eger Cart ishinde bul prooduct ushin cartitem bar bolsa, oni update qilamiz"""
            existing_item.quantity = new_quantity
            existing_item.save()
            data = CartItemSerializer(existing_item).data
        else:
            new_item = serializer.save(cart=cart)
            data = CartItemSerializer(new_item).data

        return success_response(data=data, status_code=status.HTTP_201_CREATED)
    


    @extend_schema(
        tags=['Cart'],
        request=CartItemSerializer,
        responses={
            200: wrapped_response(CartItemSerializer),
            400: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.filter(cart=cart)

        page_data = paginate_queryset(cart_item, request)
        data = {
            'results': CartItemSerializer(page_data['results'], many=True).data,
            'pagination': page_data['pagination'],
        }
        return success_response(data=data)
    

class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cart'],
        responses={
            200: MessageResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, pk):
        try:
            cartitem = CartItem.objects.get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return error_response("CartItem not found", status.HTTP_404_NOT_FOUND)
        
        cartitem.delete()
        return success_response(
            data={'message': 'CartItem deleted successfully'}
        )


    





class OrderCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Order'],
        request=OrderCreateSerializer,
        responses={
            201: wrapped_response(OrderSerializer),
            400: ErrorResponseSerializer,
        },
    )

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        address = serializer.validated_data.get('address')
        # Dublikat ID lardi oshirdemiz (Misal: [1, 2, 2] kelse [1, 2] boladi)
        cart_item_ids = list(set(serializer.validated_data.get('cart_item_ids')))

        user = request.user
        cart = Cart.objects.get(user=user)

        # Tranzaksiya baslandi (Hammesi saqlanadi yamasa hammesi izge qaytadi)
        try:
            with transaction.atomic():
                
                # Optimal bazaga murajat etiw (tek bir marte isleydi)
                # select_related - Product-lardi qosip alip keledi JOIN qilip
                # select_for_update - tek saylangan Product-lardi bloklap turadi (select_related arqali join qilinganlar)
                # order_by - id boyinsha tartipleydi
                # list - list bolgani ushin buyruq tap usi jerde, tap hazir orinlanadi (product bloklanadi)
                cart_items = list(
                    CartItem.objects.select_related('product')  
                    .select_for_update(of=('product',))
                    .filter(cart=cart, id__in=cart_item_ids)
                    .order_by('product__id')
                )

                # Tekseriw (Validatsiya)
                if not cart_items:
                    raise ValidationError({"cart": "Saylangan CartITem-lar sizdin Cart ishinen tawilmadi yamasa sebet bos"})
                    
                if len(cart_items) != len(cart_item_ids): # jiberilgen IDlar menen aniqlangan IDlar ten emes bolsa
                     raise ValidationError({"cart_item_ids": "Ayrim CartItem-lar tawilmadi yamasa sizge tiyisli emes."})

                # ORDER jaratiw (total_price hazirshe 0 ge ten)
                order = Order.objects.create(
                    user=user,
                    total_price=Decimal('0.00'),
                    address=address,
                    status=Order.Status.PENDING     # kutilmekte
                )

                total_price = Decimal('0.00')

                # Sikl ishinde esaplaw ham saqlaw
                for item in cart_items:
                    product = item.product

                    """Bazadagi Product stock tekseriw
                    CartItem jaratilgan keyin product.stock azaygan boliwi mumkin
                    """
                    if item.quantity > product.stock:
                        raise ValidationError({
                            "stock": f"Keshiresiz, '{product.name}' atli producttan bazada {product.stock} dana qalgan."
                        })

                    # Bahasin esaplaw
                    price = product.get_price_or_discount_price()
                    total_price += price * item.quantity

                    # OrderItem jaratiw 
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=price
                    )

                    # Product stock azaytiw
                    product.stock -= item.quantity
                    product.save()

                # en songi total_price saqlaw
                order.total_price = total_price
                order.save()

                # Satip alingan product-lardi oshiriw CatItemlardi
                CartItem.objects.filter(id__in=[item.id for item in cart_items]).delete()

            # Tranzaksiya tabisli tamanlandi
            data = OrderSerializer(order).data
            return success_response(data=data, status_code=status.HTTP_201_CREATED)

        except Exception as e:
            # Eger ValidationError bolsa onin ozin JSON qilip qaytaradi
            if isinstance(e, ValidationError):
                raise e
            # Basqa bir kutilmegen qatelikler ushin 
            return error_response(f"Buyirtpa jaratiwda qatelik juz berdi: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
    

    @extend_schema(
        tags=['Order'],
        responses={
            200: wrapped_response(CartItemSerializer),
            400: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        order = Order.objects.filter(user=request.user)
        page_data = paginate_queryset(order, request)
        data = {
            'results': OrderSerializer(page_data['results'], many=True).data,
            'pagination': page_data['pagination'],
        }
        return success_response(data=data)



class OrderPayView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Order'],
        responses={
            200: OrderSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request, pk):

        with transaction.atomic():
            """ Tek gana tanlangan Order ID  lock boladi """
            order = get_object_or_404(Order.objects.select_for_update(), id=pk, user=request.user)
            
            if order.status != Order.Status.PENDING:
                return error_response("Buyurtpa ushin tolem qila almaysiz yamasan tolengen", status_code=status.HTTP_400_BAD_REQUEST)
            
            order.status = Order.Status.PAID
            order.save()
            
        data = OrderSerializer(order).data
        return success_response(data=data, status_code=status.HTTP_200_OK)


""" post, get, delete"""

class ReviewCreateGetView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Review'],
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data.get('product')

        """ user bul productqa aldin review qaldirganba? """
        if Review.objects.filter(user=request.user, product=product).exists():
            return error_response(
                "Bul product ushin aldin comment qaldirgansiz. Tek bir marte comment jaziw mumkin",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        order_status = [Order.Status.PAID, Order.Status.SHIPPED]
        is_bought = OrderItem.objects.filter(
            order__user=request.user, 
            product=product, 
            order__status__in=order_status
            ).exists()
        
        """ user satip algan product-qa review jazip atirma? """
        if not is_bought:
            return error_response(
                "Siz bul productqa komment qaldiriw ushin, oni satip algan boliwiniz kerek",
                status_code=status.HTTP_400_BAD_REQUEST
                )
        
        """ Review jaratildi, user-di request userden alip jiberdim """
        serializer.save(user=request.user)  # Review obyektin save qilamiz
    
        return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
    

    @extend_schema(
        tags=['Review'],
        responses={
            200: ReviewSerializer(many=True),
            400: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)


    
class ReviewDeleteView(APIView):
    
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Review'],
        responses={
            200: ReviewSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
        except Review.DoesNotExist:
            return error_response("Review not found", status.HTTP_404_NOT_FOUND)
        
        review.delete()
        return success_response(
            data={'message': 'Review deleted successfully'}
        )



    
class ReviewListProduct(APIView):
    """ Belgili bir product ushin qaldirilgan aqirdi 5 dana kommentariyani ko   riw """

    @extend_schema(
        tags=['Review'],
        responses={
            200: ReviewSerializer(many=True),
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, pk):

        """ Bunday ID-dagi product barma? """
        if not Product.objects.filter(id=pk).exists():
            return error_response(
                "Bunday ID dagi product tawilmadi",
                status_code=status.HTTP_404_NOT_FOUND
            )

        """ Usi product ushin Review-lardi islep taw, -created_at boyinsha taqla ham aqirgi 5 ajratip al """
        reviews = Review.objects.filter(product_id=pk).order_by('-created_at')[:5]
        serializer = ReviewSerializer(reviews, many=True)

        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)
    



        
        
