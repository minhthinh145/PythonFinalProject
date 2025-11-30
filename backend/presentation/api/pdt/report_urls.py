from django.urls import path
from .report_views import (
    OverviewStatsView, KhoaStatsView, NganhStatsView, 
    GiangVienStatsView, ExportExcelView, ExportPDFView
)

urlpatterns = [
    path('overview', OverviewStatsView.as_view(), name='report-overview'),
    path('dk-theo-khoa', KhoaStatsView.as_view(), name='report-khoa'),
    path('dk-theo-nganh', NganhStatsView.as_view(), name='report-nganh'),
    path('tai-giang-vien', GiangVienStatsView.as_view(), name='report-giang-vien'),
    path('export/excel', ExportExcelView.as_view(), name='report-export-excel'),
    path('export/pdf', ExportPDFView.as_view(), name='report-export-pdf'),
]
