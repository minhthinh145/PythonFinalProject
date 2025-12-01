"""
Common API URL Configuration
"""
from django.urls import path
from .views import GetHocKyHienHanhView, GetDanhSachNganhView

urlpatterns = [
    path('hoc-ky-hien-hanh', GetHocKyHienHanhView.as_view(), name='hoc-ky-hien-hanh'),
    path('hien-hanh', GetHocKyHienHanhView.as_view(), name='hien-hanh'),  # Alias for FE compatibility
    path('dm/nganh', GetDanhSachNganhView.as_view(), name='danh-sach-nganh'),
]
