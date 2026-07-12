from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


urlpatterns = [
    
    # Simple JWT standart endpointlari:
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 

    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('create/', views.UserCreateView.as_view(), name='auth-create'),
    path('me/', views.MeView.as_view(), name='auth-me'),
]