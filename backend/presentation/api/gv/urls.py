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
)

urlpatterns = [
    # Lop Hoc Phan
    path('lop-hoc-phan', GVLopHocPhanListView.as_view(), name='gv-lhp-list'),
    path('lop-hoc-phan/<str:lhp_id>', GVLopHocPhanDetailView.as_view(), name='gv-lhp-detail'),
    path('lop-hoc-phan/<str:lhp_id>/sinh-vien', GVLopHocPhanStudentsView.as_view(), name='gv-lhp-students'),
    path('lop-hoc-phan/<str:lhp_id>/diem', GVLopHocPhanGradesView.as_view(), name='gv-lhp-grades'),
    
    # TKB Weekly
    path('tkb-weekly', GVTKBWeeklyView.as_view(), name='gv-tkb-weekly'),
]
