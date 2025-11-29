"""
Enrollment API URLs
"""
from django.urls import path
from .views import (
    CheckGhiDanhStatusView,
    GetMonHocGhiDanhView,
    GhiDanhMonHocView,
    GetDanhSachDaGhiDanhView
)

urlpatterns = [
    path('check-ghi-danh', CheckGhiDanhStatusView.as_view(), name='check-ghi-danh'),
    path('mon-hoc-ghi-danh', GetMonHocGhiDanhView.as_view(), name='mon-hoc-ghi-danh'),
    path('ghi-danh', GhiDanhMonHocView.as_view(), name='ghi-danh'),
    path('ghi-danh/my', GetDanhSachDaGhiDanhView.as_view(), name='da-ghi-danh'),
]
