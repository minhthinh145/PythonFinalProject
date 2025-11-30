from typing import List, Dict, Any
from application.enrollment.interfaces.repositories import IKhoaRepository

class GetDanhSachKhoaUseCase:
    def __init__(self, khoa_repo: IKhoaRepository):
        self.khoa_repo = khoa_repo

    def execute(self) -> Dict[str, Any]:
        khoa_list = self.khoa_repo.get_all()
        
        data = [
            {
                "id": str(k.id),
                "maKhoa": k.ma_khoa,
                "tenKhoa": k.ten_khoa
            }
            for k in khoa_list
        ]
        
        return {
            "isSuccess": True,
            "data": data,
            "message": "Lấy danh sách khoa thành công"
        }
