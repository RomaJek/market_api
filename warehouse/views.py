# Create your views here.


from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models import Case, When, F, DecimalField
from rest_framework.parsers import MultiPartParser, FormParser  # image ushin kerek swagerde 
from rest_framework.response import Response


from .models import Product, Category
from core.pagination import paginate_queryset
from .serializers import (
    ProductSerializer, 
    CategorySearchSerializer, 
    CategorySerializer,
    CategoryListSerializer,

    ProductCreateSerializer,
    ProductUpdateSerializer

    )

from core.schema import (
    wrapped_response,
    ErrorResponseSerializer,
    MessageResponseSerializer,
)

from core.response import error_response, success_response
from accounts.permissions import IsAuthenticated, IsAdminOrSuperAdmin



def get_all_category_ids(category_id):
    """
    Kiritilgen category_id ham onin hamme child, grandchild 
    categorylarinin ID larin list qilib qaytaradi
    """
    category_ids = set([int(category_id)])
    current_ids =[int(category_id)]

    # Har bir category darejesi (level) boyinsha tomenge tusip baramiz
    while current_ids:
        children = Category.objects.filter(parent_id__in=current_ids).values_list('id', flat=True)
        """
        parent_id__in=current_ids  -> parent_id-si current_ids listi ishinde bar bolgan hamme category-lardi shigarip aladi
        Misali: current_ids[2, 1, 3]  demek parent-id-si [2, 1, 3] ge ten bolgan hamme categorylardi birden shigip keledi.
        Birew emes bir neshe parent-lardin child-larin birden shigarip atirman.
        skil menen birimlep listti aylandiriw shart emes.

        .values_list('id')  -> filterden shiqqan objectlar ishinen tek ID-di ajratip aladi
        flat=True  -> ajratip alingan ID-lardi list korinisine aylantirip beredi. Misali: [2, 1, 4]
        """

        if not children:
            break

        category_ids.update(children)
        current_ids = list(children)
    
    return list(category_ids)   # setti listke aylandirip jiberdi














class ProductsView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=['Products'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=str,
                required=False,
                description='Filter by product name'
            ),
            OpenApiParameter(
                name='category',
                type=int,
                required=False,
                description='Filter by product category'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.NUMBER,
                required=False,
                description='Product max price'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.NUMBER,
                required=False,
                description='Product min price'
            ),
            OpenApiParameter(
                name='page',
                type=int,
                required=False,
                description='Page number (default: 1)',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                required=False,
                description='Items per page (default: 10, max: 100)',
            ),
        ],
        responses={
            200: wrapped_response(ProductSerializer)
        },

    )

    def get(self, request):
        """ (Multi-parameter search) Productti ko'p parametrler menen izler """
        products = Product.objects.filter(stock__gt=0, is_active=True)
        name = request.query_params.get('name')
        category = request.query_params.get('category')
        max_price = request.query_params.get('max_price')
        min_price = request.query_params.get('min_price')

        if max_price and min_price:
            if Decimal(max_price) < Decimal(min_price):
                return error_response(message="min_price ulken bola almaydi max_price-dan")

        if name:
            products = products.filter(name__icontains=name)    # ulken kishige qaramay tekserdei
        
        if category:
            products = products.filter(category_id=category)

        



        if max_price or min_price:   
            # misal: user soradi max=20 izledi. product: discount_price=19, price=25. tek price qarap sortlaw qate bolar edi 
            products = products.annotate(   # qosimsha coloumn (bagana) real emes. yadda saqlangan bagana 
                final_price=Case(
                    When(discount_price__gt=0, then=F('discount_price')),   # descount_price > 0 soni aladi
                    default=F('price'), # yamasa defualt jagdayda pricedin ozin aladi
                    output_field=DecimalField() # Decimal tipinde saqlaydi
                )
        # haqiqiy product bahasin userge tusinikli qilip shigariw ushin
            )
        if max_price:
            products = products.filter(final_price__lte=Decimal(max_price)).order_by('final_price')
        
        if min_price:
            products = products.filter(final_price__gte=Decimal(min_price)).order_by('final_price')

        """ 
            __gte = Greater Than or Equal (>=)
            __gt = Greater Than (>)
        """

        page_data = paginate_queryset(products, request)

        data = {
            'results': ProductSerializer(page_data['results'], many=True).data,
            'pagination': page_data['pagination'],
        }
        return success_response(data=data)





    @extend_schema(
        tags=['Products'],
        # request=ProductCreateSerializer,
        request={
        'multipart/form-data': ProductCreateSerializer
        },
        responses={
            201: ProductSerializer,
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        """ Tek gana admin, superadmin product qosa aladi """
        permission = IsAdminOrSuperAdmin()
        if not permission.has_permission(request, self):
            return error_response(
                message='Permission denied. Only Admin or SuperAdmin can create products.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
 
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='Validation error.',
                fields=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
 
        product = serializer.save()
        return success_response(
            data=ProductSerializer(product).data,
            status_code=status.HTTP_201_CREATED,
        )
 
 





    



class ProductIDView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    # GET - hamme ushin 
    @extend_schema(
            tags=['Products'],
            responses={
                200: ProductSerializer,
                404: ErrorResponseSerializer,
            },
        )
    def get(self, request, pk):

        product = get_object_or_404(Product, id=pk)
        serializer = ProductSerializer(product)

        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)


    # PATCH - admin, superadmin
    @extend_schema(
        tags=['Products'],
        request=ProductUpdateSerializer,
        responses={
            200: ProductSerializer,
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def patch(self, request, pk):
        permission = IsAdminOrSuperAdmin()
        if not permission.has_permission(request, self):
            return error_response(
                message='Permission denied. Only Admin or SuperAdmin can update products.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
 
        product = get_object_or_404(Product, id=pk)
        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
 
        if not serializer.is_valid():
            return error_response(
                message='Validation error.',
                fields=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
 
        updated_product = serializer.save()
        return success_response(
            data=ProductSerializer(updated_product).data,
            status_code=status.HTTP_200_OK,
        )

 
    # DELETE - admin, superadmin
    @extend_schema(
        tags=['Products'],
        responses={
            200: MessageResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, pk):
        permission = IsAdminOrSuperAdmin()
        if not permission.has_permission(request, self):
            return error_response(
                message='Permission denied. Only Admin or SuperAdmin can delete products.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
 
        product = get_object_or_404(Product, id=pk)
        product_name = product.name
        product.delete()
 
        return success_response(
            data={'message': f"Product '{product_name}' successfully deleted."},
            status_code=status.HTTP_200_OK,
        )
 






 




class CategorySearchView(APIView):
    @extend_schema(
        tags=['Products'],
        request=CategorySearchSerializer,
        responses={
            200: CategorySearchSerializer,
            400: ErrorResponseSerializer,
        },
    )

    def post(self, request):
        """ Categorydi name boyinsha izlew. """
        serializer = CategorySearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        search_name = params.get('name', '')

        if search_name:
            category = Category.objects.filter(name__istartswith=search_name)
        else:
            category = ''

        page_data = paginate_queryset(category, page_number=params.get('page'), page_size=params.get('page_size'))

        data = {
            'results': CategorySerializer(page_data['results'], many=True).data,
            'pagination': page_data['pagination'],
        }

        return success_response(data=data)


    

class CategoryListView(APIView):
    @extend_schema(
        tags=['Products'],
        request=CategoryListSerializer,
        responses={
            200: CategoryListSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        """ Berilgen Parent ID ga ten bolgan Categorylardi shigaradi eger ID kelmese Parenti joq Categorylardi shigaradi. Bul Category arqali Productlar katalogin ko'riwge jardem beredi """
        serializer = CategoryListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        category_id = params.get('id', '')     # id joq bolsa, '' pustoy tirnaqshani aladi

        if category_id:
            categories = Category.objects.filter(parent=category_id)
        else:
            categories = Category.objects.filter(parent__isnull=True) 
        
        page_data = paginate_queryset(categories, page_number=params.get('page'), page_size=params.get('page_size'))

        data = {
            'results': CategorySerializer(page_data['results'], many=True).data,
            'pagination': page_data['pagination'],
        }

        return success_response(data=data)
        
