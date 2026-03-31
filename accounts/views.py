from django.shortcuts import render

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError



from .models import User
from .permissions import IsAuthenticated
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    LoginSerializer,
    UpdateProfileSerializer,
)


from core.schema import (
    wrapped_response,
    ErrorResponseSerializer,
    MessageResponseSerializer,
)

from core.response import error_response, success_response


# UserResponse = wrapped_response(UserSerializer)




def set_auth_cookies(response, access_token, refresh_token):
    """ Token-di browser cookie-inda saqlar ushin """
    is_secure = not settings.DEBUG  # settings ishinde DEBUG False bolsa https arqali isleydi. True bolsa localda http isleydi
    access_max_age = int(   # settings-tagi waqitlardi alip sekontqa aylantiradi. waqit pitkenen keyin oship ketedi
        settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    )
    refresh_max_age = int(
        settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
    )

    samesite = 'None' if is_secure else 'Lax'
    """    
    'Lax'- http. tek sol sayttan cookie jiberedi. Basqa jerdegi Link ustine bassa cookie jiberedi. Misal uchin backend ham fronend bir domainde bolsa. Basqa saytlarga cookie bermeydi.
    'None'- https. basqa saytlargada cookie jiberdei. Link ustin basqanda, frontend basqa domende bolganda
    'Strict'- https. TEK GANA cookie tiyisli bolgan sayttan kirgende isleydi. Basqa jerdegi Link ustine bassa cookie jibermeydi.
    """
    
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE,
        value=str(access_token),
        max_age=access_max_age,
        httponly=True,  # cookie-di JavaScript urlay almawi ushin 
        secure=is_secure,   # cookie-di https arqali jiberi ushin (secure=True)
        samesite=samesite,  # None, Lax, Strict usi 3 rejimden birewi saylanadi
    )

    response.set_cookie(    # browser cookiena saqlaw
        key=settings.REFRESH_TOKEN_COOKIE,
        value=str(refresh_token),
        max_age=refresh_max_age,
        httponly=True,
        secure=is_secure,
        samesite=samesite,
        path='/api/auth/refresh',   # tek usi endpointqa murajat etkende refresh tokendi jiberiw ushin, basqalarina jibermeydi.
    )


def clear_auth_cookies(response):
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
    response.delete_cookie(
        settings.REFRESH_TOKEN_COOKIE,
        path='/api/auth/refresh',
    )



class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Auth'],
        request=LoginSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
        },
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        response = success_response(
            data={
                'message': 'Login successful.'
            }
        )
        set_auth_cookies(response, refresh.access_token, refresh)

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        request=None,
        responses={200: MessageResponseSerializer},
    )

    def post(self, request):
        response = success_response(data={'message': 'Logout successful.'})
        clear_auth_cookies(response)

        raw_refresh = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE)
        if raw_refresh:
            try:
                token = RefreshToken(raw_refresh)
                token.blacklist()
            except (TokenError, AttributeError):
                pass
        return response
        



class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Auth'],
        request=None,
        responses={
            200: MessageResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE)

        if not raw_refresh:
            return error_response('Refresh token not found.', status.HTTP_401_UNAUTHORIZED)

        try:
            old_refresh = RefreshToken(raw_refresh)
            user_id = old_refresh.payload.get('user_id')
            old_refresh.blacklist()
        except (TokenError, AttributeError):
            response = error_response(
                'Invalid or expired refresh token.',
                status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response = error_response('User not found.', status.HTTP_401_UNAUTHORIZED)
            clear_auth_cookies(response)
            return response

        new_refresh = RefreshToken.for_user(user)

        response = success_response(data={'message': 'Token refreshed.'})
        set_auth_cookies(response, new_refresh.access_token, new_refresh)

        return response




class UserCreateView(APIView):

    @extend_schema(
            tags=['Profile'],
            request = CreateUserSerializer,
            responses={
                201: wrapped_response(UserSerializer),
                400: ErrorResponseSerializer
            },
    )

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        data = UserSerializer(new_user).data
        return success_response(data=data, status_code=status.HTTP_201_CREATED)



class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Profile'],
        responses={200: wrapped_response(UserSerializer)},
    )
    def get(self, request):
        data = UserSerializer(request.user).data
        return success_response(data=data)
    
    @extend_schema(
        tags=['Profile'],
        request=UpdateProfileSerializer,
        responses={
            200: wrapped_response(UserSerializer),
            400: ErrorResponseSerializer,
        },
    )
    def patch(self, request):
        serialzier = UpdateProfileSerializer(
            instance=request.user,
            data=request.data,
            partial=True,   # tek ozgertiw kerek field-lardi jiberiwge ruxsat beredi, hammesin sorap ootirmaydi
        )
        serialzier.is_valid(raise_exception=True)
        serialzier.save()

        data = UserSerializer(request.user).data
        return success_response(data=data)



class UserListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        data = UserSerializer(users, many=True).data
        return success_response(data=data, status_code=status.HTTP_200_OK)






