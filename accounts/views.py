from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken


from .models import User
from .permissions import IsAuthenticated
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    LogoutSerializer
)

from core.schema import (
    wrapped_response,
    ErrorResponseSerializer,
    MessageResponseSerializer,
)

from core.response import error_response, success_response


class LogoutView(APIView):
    # Tek gana saytqa kirgen user sayttan shiga aladi
    permission_classes = [IsAuthenticated]

    @extend_schema(
            request = LogoutSerializer,
            responses={
                205: MessageResponseSerializer,# wrapped_response(MessageSerializer),
                400: ErrorResponseSerializer
            },
        )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Validatsiyadan otken tokendi alamiz
            refresh_token = serializer.validated_data["refresh_token"]
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response(
                {"message": "Sayttan shiqtiniz."}, 
                status_code=status.HTTP_200_OK
                # status_code=status.HTTP_205_RESET_CONTENT  # negizi usi isletiw kerekedi, biraq djson qaytarmadi
            )
        except Exception as e:
            return error_response(
                "Token xate yamasa muddeti otken.", 
                status_code=status.HTTP_400_BAD_REQUEST
            )




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
        responses={
            200: wrapped_response(UserSerializer),
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            },
    )
    def get(self, request):
        data = UserSerializer(request.user).data
        return success_response(data=data)

    
    @extend_schema(
        tags=['Profile'],
        request=UpdateProfileSerializer,
        responses={
            200: wrapped_response(UserSerializer),
            401: ErrorResponseSerializer,
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







