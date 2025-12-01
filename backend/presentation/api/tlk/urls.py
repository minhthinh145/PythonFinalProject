"""
TLK (Tro Ly Khoa) API URLs
"""
from django.urls import path
from .views import (
    TLKMonHocView,
    TLKGiangVienView,
    TLKHocPhansForCreateLopView,
    TLKPhongHocView,
    TLKAvailablePhongHocView,
    TLKDeXuatHocPhanView,
    TLKThoiKhoaBieuBatchView,
    TLKXepThoiKhoaBieuView,
)

urlpatterns = [
    path('mon-hoc', TLKMonHocView.as_view(), name='tlk-mon-hoc'),
    path('giang-vien', TLKGiangVienView.as_view(), name='tlk-giang-vien'),
    path('lop-hoc-phan/get-hoc-phan/<str:hoc_ky_id>', TLKHocPhansForCreateLopView.as_view(), name='tlk-get-hoc-phans-for-create-lop'),
    path('phong-hoc', TLKPhongHocView.as_view(), name='tlk-phong-hoc'),
    path('phong-hoc/available', TLKAvailablePhongHocView.as_view(), name='tlk-available-phong-hoc'),
    # New TLK APIs
    path('de-xuat-hoc-phan', TLKDeXuatHocPhanView.as_view(), name='tlk-de-xuat-hoc-phan'),
    path('thoi-khoa-bieu/batch', TLKThoiKhoaBieuBatchView.as_view(), name='tlk-tkb-batch'),
    path('thoi-khoa-bieu', TLKXepThoiKhoaBieuView.as_view(), name='tlk-xep-tkb'),
]
