"""
GV (Giang Vien) Module - Repository Interfaces & DTOs
"""
from .repositories import (
    IGVLopHocPhanRepository,
    IGVGradeRepository,
    IGVTKBRepository,
    GVLopHocPhanDTO,
    GVLopHocPhanDetailDTO,
    GVStudentDTO,
    GVGradeDTO,
    GVTKBItemDTO,
)

__all__ = [
    'IGVLopHocPhanRepository',
    'IGVGradeRepository', 
    'IGVTKBRepository',
    'GVLopHocPhanDTO',
    'GVLopHocPhanDetailDTO',
    'GVStudentDTO',
    'GVGradeDTO',
    'GVTKBItemDTO',
]
