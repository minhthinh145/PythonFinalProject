from django.urls import path
from .views import (
    SetHocKyHienHanhView, CreateBulkKyPhaseView, GetPhasesByHocKyView,
    UpdateDotGhiDanhView, GetDotGhiDanhByHocKyView, DotDangKyView,
    GetDanhSachKhoaView
)
from .course_proposal_view import CourseProposalView
from .room_views import (
    AvailableRoomView, RoomByKhoaView, AssignRoomView, UnassignRoomView
)
from .tuition_views import TuitionPolicyView, CalculateTuitionView

urlpatterns = [
    path('quan-ly-hoc-ky/hoc-ky-hien-hanh', SetHocKyHienHanhView.as_view(), name='set-hoc-ky-hien-hanh'),
    path('quan-ly-hoc-ky/ky-phase/bulk', CreateBulkKyPhaseView.as_view(), name='create-bulk-ky-phase'),
    path('quan-ly-hoc-ky/ky-phase/<str:hocKyId>', GetPhasesByHocKyView.as_view(), name='get-phases-by-hoc-ky'),
    path('de-xuat-hoc-phan', CourseProposalView.as_view(), name='course-proposal-list'),
    path('de-xuat-hoc-phan/duyet', CourseProposalView.as_view(), name='course-proposal-approve'),
    path('de-xuat-hoc-phan/tu-choi', CourseProposalView.as_view(), name='course-proposal-reject'),
    path('dot-ghi-danh/update', UpdateDotGhiDanhView.as_view(), name='update-dot-ghi-danh'),
    path('dot-dang-ky/<str:hocKyId>', GetDotGhiDanhByHocKyView.as_view(), name='get-dot-ghi-danh-by-hoc-ky'),
    path('dot-dang-ky', DotDangKyView.as_view(), name='dot-dang-ky'),
    path('khoa', GetDanhSachKhoaView.as_view(), name='get-danh-sach-khoa'),
    path('phong-hoc/available', AvailableRoomView.as_view(), name='get-available-rooms'),
    path('phong-hoc/khoa/<str:khoaId>', RoomByKhoaView.as_view(), name='get-rooms-by-khoa'),
    path('phong-hoc/assign', AssignRoomView.as_view(), name='assign-room'),
    path('phong-hoc/unassign', UnassignRoomView.as_view(), name='unassign-room'),
    path('hoc-phi/chinh-sach', TuitionPolicyView.as_view(), name='tuition-policy-list-create'),
    path('hoc-phi/chinh-sach/<str:id>', TuitionPolicyView.as_view(), name='tuition-policy-update'),
    path('hoc-phi/tinh-toan-hang-loat', CalculateTuitionView.as_view(), name='calculate-tuition-bulk'),
]
