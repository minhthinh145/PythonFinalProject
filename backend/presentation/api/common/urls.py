"""
Common API URL Configuration
"""
from django.urls import path
from .views import GetHocKyHienHanhView, GetDanhSachNganhView, GetDanhSachKhoaView, GetNganhChuaCoChinhSachView
from .config_views import ConfigTietHocView
from presentation.api.pdt.views import UpdateHocKyDatesView

urlpatterns = [
    path('hoc-ky-hien-hanh', GetHocKyHienHanhView.as_view(), name='hoc-ky-hien-hanh'),
    path('hien-hanh', GetHocKyHienHanhView.as_view(), name='hien-hanh'),  # Alias for FE compatibility
    path('hoc-ky/dates', UpdateHocKyDatesView.as_view(), name='update-hoc-ky-dates'),  # Update semester dates
    path('dm/nganh/chua-co-chinh-sach', GetNganhChuaCoChinhSachView.as_view(), name='nganh-chua-co-chinh-sach'),  # Must be before dm/nganh
    path('dm/nganh', GetDanhSachNganhView.as_view(), name='danh-sach-nganh'),
    path('dm/khoa', GetDanhSachKhoaView.as_view(), name='danh-sach-khoa'),
    path('config/tiet-hoc', ConfigTietHocView.as_view(), name='config-tiet-hoc'),
]

