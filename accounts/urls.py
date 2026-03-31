from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('refresh/', views.RefreshView.as_view(), name='auth-refresh'),
    path('create/', views.UserCreateView.as_view(), name='auth-create'),
    path('user/list', views.UserListView.as_view(), name='auth-user-list'),
    path('me/', views.MeView.as_view(), name='auth-me'),
]