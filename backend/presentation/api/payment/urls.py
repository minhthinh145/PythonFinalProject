"""
Payment API URLs
"""
from django.urls import path
from .views import CreatePaymentView, GetPaymentStatusView, PaymentIPNView

urlpatterns = [
    path('create', CreatePaymentView.as_view(), name='payment-create'),
    path('status', GetPaymentStatusView.as_view(), name='payment-status'),
    path('ipn', PaymentIPNView.as_view(), name='payment-ipn'),
]
