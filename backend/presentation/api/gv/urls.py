"""
GV API URLs
"""
from django.urls import path
from .views import (
    GVLopHocPhanListView,
    GVLopHocPhanDetailView,
    GVLopHocPhanStudentsView,
    GVLopHocPhanGradesView,
    GVTKBWeeklyView,
    GVTaiLieuListView,
    GVTaiLieuUploadView,
    GVTaiLieuDetailView,
    GVTaiLieuDownloadView,
)

urlpatterns = [
    # Lop Hoc Phan
    path('lop-hoc-phan', GVLopHocPhanListView.as_view(), name='gv-lhp-list'),
    path('lop-hoc-phan/<str:lhp_id>', GVLopHocPhanDetailView.as_view(), name='gv-lhp-detail'),
    path('lop-hoc-phan/<str:lhp_id>/sinh-vien', GVLopHocPhanStudentsView.as_view(), name='gv-lhp-students'),
    path('lop-hoc-phan/<str:lhp_id>/diem', GVLopHocPhanGradesView.as_view(), name='gv-lhp-grades'),
    
    # TaiLieu (Documents)
    path('lop-hoc-phan/<str:lhp_id>/tai-lieu', GVTaiLieuListView.as_view(), name='gv-tailieu-list'),
    path('lop-hoc-phan/<str:lhp_id>/tai-lieu/upload', GVTaiLieuUploadView.as_view(), name='gv-tailieu-upload'),
    path('lop-hoc-phan/<str:lhp_id>/tai-lieu/<str:doc_id>', GVTaiLieuDetailView.as_view(), name='gv-tailieu-detail'),
    path('lop-hoc-phan/<str:lhp_id>/tai-lieu/<str:doc_id>/download', GVTaiLieuDownloadView.as_view(), name='gv-tailieu-download'),
    
    # TKB Weekly
    path('tkb-weekly', GVTKBWeeklyView.as_view(), name='gv-tkb-weekly'),
]
    