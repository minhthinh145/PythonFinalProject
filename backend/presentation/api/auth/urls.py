"""
Auth API URLs
Map 1-1 với frontend API endpoints
"""
from django.urls import path
from .auth_views import LoginView, RefreshTokenView

urlpatterns = [
    path('login', LoginView.as_view(), name='auth-login'),
    path('refresh', RefreshTokenView.as_view(), name='auth-refresh'),
]
