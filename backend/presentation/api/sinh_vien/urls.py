"""
SinhVien API URLs
"""
from django.urls import path
from .views import SinhVienProfileView

urlpatterns = [
    path('profile', SinhVienProfileView.as_view(), name='sv-profile'),
]
