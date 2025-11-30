"""
Course Registration API URLs
"""
from django.urls import path
from .views import (
    CheckPhaseDangKyView, 
    GetDanhSachLopHocPhanView, 
    GetDanhSachLopDaDangKyView,
    DangKyLopHocPhanView,
    HuyDangKyLopHocPhanView,
    DangKyLopHocPhanView,
    HuyDangKyLopHocPhanView,
    ChuyenLopHocPhanView,
    GetLopChuaDangKyByMonHocView,
    GetLichSuDangKyView,
    GetTKBWeeklyView,
    TraCuuHocPhanView,
    GetChiTietHocPhiView
)

urlpatterns = [
    path('check-phase-dang-ky', CheckPhaseDangKyView.as_view(), name='check-phase-dang-ky'),
    path('lop-hoc-phan', GetDanhSachLopHocPhanView.as_view(), name='lop-hoc-phan'),
    path('lop-da-dang-ky', GetDanhSachLopDaDangKyView.as_view(), name='lop-da-dang-ky'),
    path('dang-ky-hoc-phan', DangKyLopHocPhanView.as_view(), name='dang-ky-hoc-phan'),
    path('huy-dang-ky-hoc-phan', HuyDangKyLopHocPhanView.as_view(), name='huy-dang-ky-hoc-phan'),
    path('chuyen-lop-hoc-phan', ChuyenLopHocPhanView.as_view(), name='chuyen-lop-hoc-phan'),
    path('lop-hoc-phan/mon-hoc', GetLopChuaDangKyByMonHocView.as_view(), name='lop-chua-dang-ky-by-mon-hoc'),
    path('lich-su-dang-ky', GetLichSuDangKyView.as_view(), name='lich-su-dang-ky'),
    path('tkb-weekly', GetTKBWeeklyView.as_view(), name='tkb-weekly'),
    path('tra-cuu-hoc-phan', TraCuuHocPhanView.as_view(), name='tra-cuu-hoc-phan'),
    path('hoc-phi', GetChiTietHocPhiView.as_view(), name='hoc-phi'),
]
