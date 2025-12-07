"""
SinhVien API URLs
"""
from django.urls import path
from .views import (
    SinhVienProfileView,
    SVTaiLieuListView,
    SVTaiLieuDownloadView,
)

urlpatterns = [
    path('profile', SinhVienProfileView.as_view(), name='sv-profile'),
    
    # TaiLieu (Documents)
    path('lop-hoc-phan/<str:lhp_id>/tai-lieu', SVTaiLieuListView.as_view(), name='sv-tailieu-list'),
    path('lop-hoc-phan/<str:lhp_id>/tai-lieu/<str:doc_id>/download', SVTaiLieuDownloadView.as_view(), name='sv-tailieu-download'),
]
