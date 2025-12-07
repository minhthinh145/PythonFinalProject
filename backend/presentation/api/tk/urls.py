"""
TK (Truong Khoa) API URLs
"""
from django.urls import path
from .views import (
    TKDeXuatHocPhanView,
    TKDuyetDeXuatView,
    TKTuChoiDeXuatView,
)

urlpatterns = [
    path('de-xuat-hoc-phan', TKDeXuatHocPhanView.as_view(), name='tk-de-xuat-hoc-phan'),
    path('de-xuat-hoc-phan/duyet', TKDuyetDeXuatView.as_view(), name='tk-duyet-de-xuat'),
    path('de-xuat-hoc-phan/tu-choi', TKTuChoiDeXuatView.as_view(), name='tk-tu-choi-de-xuat'),
]
