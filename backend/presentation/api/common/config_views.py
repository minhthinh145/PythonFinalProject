from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class ConfigTietHocView(APIView):
    """
    GET /api/config/tiet-hoc
    Return configuration for class periods (tiet hoc)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Hardcoded configuration based on typical university schedule
        # Can be moved to DB or settings later
        tiet_hoc_config = [
            {"tiet": 1, "start": "07:00", "end": "07:50"},
            {"tiet": 2, "start": "07:50", "end": "08:40"},
            {"tiet": 3, "start": "09:00", "end": "09:50"},
            {"tiet": 4, "start": "09:50", "end": "10:40"},
            {"tiet": 5, "start": "10:40", "end": "11:30"},
            {"tiet": 6, "start": "13:00", "end": "13:50"},
            {"tiet": 7, "start": "13:50", "end": "14:40"},
            {"tiet": 8, "start": "15:00", "end": "15:50"},
            {"tiet": 9, "start": "15:50", "end": "16:40"},
            {"tiet": 10, "start": "16:40", "end": "17:30"},
            {"tiet": 11, "start": "17:40", "end": "18:30"},
            {"tiet": 12, "start": "18:30", "end": "19:20"},
            {"tiet": 13, "start": "19:20", "end": "20:10"},
            {"tiet": 14, "start": "20:10", "end": "21:00"},
            {"tiet": 15, "start": "21:00", "end": "21:50"},
        ]
        
        return Response({
            "success": True,
            "data": tiet_hoc_config
        })
