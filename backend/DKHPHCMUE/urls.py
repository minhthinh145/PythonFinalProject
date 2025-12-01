"""
URL configuration for DKHPHCMUE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from presentation.api.enrollment.views import GetHocKyView
from presentation.api.pdt.tuition_views import CalculateTuitionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('presentation.api.auth.urls')),
    path('api/sv/', include('presentation.api.sinh_vien.urls')),
    path('api/sv/', include('presentation.api.enrollment.urls')),
    path('api/sv/', include('presentation.api.course_registration.urls')),
    path('api/pdt/', include('presentation.api.pdt.urls')),
    path('api/gv/', include('presentation.api.gv.urls')),  # GV Module
    path('api/tlk/', include('presentation.api.tlk.urls')),  # TLK Module
    path('api/bao-cao/', include('presentation.api.pdt.report_urls')),
    path('api/tuition/calculate-semester', CalculateTuitionView.as_view(), name='calculate-tuition-alias'),
    path('api/payment/', include('presentation.api.payment.urls')),  # Payment Module
    path('api/', include('presentation.api.common.urls')),  # Common/public APIs
    path('api/hoc-ky-nien-khoa', GetHocKyView.as_view()),  # TODO: Remove after migration
]
