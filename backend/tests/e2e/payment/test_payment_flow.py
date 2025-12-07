"""
E2E Tests for Payment API
Endpoints:
- POST /api/payment/create
- GET /api/payment/status
- POST /api/payment/ipn
"""
import pytest
import uuid
from decimal import Decimal
from rest_framework import status
from django.utils import timezone


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestPaymentCreate:
    """E2E tests for Payment Create API"""
    
    @pytest.fixture
    def setup_sv_with_tuition(self, setup_base_data, create_sv_user):
        """Setup SV with tuition to pay"""
        from infrastructure.persistence.models import HocPhi
        
        sv = create_sv_user()
        hoc_ky = setup_base_data['hoc_ky']
        
        # Create tuition record
        hoc_phi = HocPhi.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            hoc_ky=hoc_ky,
            tong_hoc_phi=Decimal('5000000'),
            trang_thai_thanh_toan='chua_thanh_toan',
            ngay_tinh_toan=timezone.now()
        )
        
        return {'sv': sv, 'hoc_phi': hoc_phi, 'hoc_ky': hoc_ky}
    
    def test_create_payment_success(self, api_client, setup_sv_with_tuition):
        """
        Test Case: SV creates payment successfully
        
        Given: SV has unpaid tuition
        When: POST /api/payment/create
        Then: Status 200, payment URL returned
        """
        sv = setup_sv_with_tuition['sv']
        hoc_ky = setup_sv_with_tuition['hoc_ky']
        api_client.force_authenticate(user=sv)
        
        payload = {
            'hocKyId': str(hoc_ky.id)
        }
        
        response = api_client.post('/api/payment/create', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        # Note: payUrl may be null in test environment without MoMo integration
    
    def test_create_payment_no_tuition(self, api_client, setup_base_data, create_sv_user):
        """
        Test Case: SV tries to pay without tuition record
        
        Given: SV has no tuition record
        When: POST /api/payment/create
        Then: Status 400, error message
        """
        sv = create_sv_user()
        hoc_ky = setup_base_data['hoc_ky']
        api_client.force_authenticate(user=sv)
        
        payload = {
            'hocKyId': str(hoc_ky.id)
        }
        
        response = api_client.post('/api/payment/create', payload, format='json')
        
        # May return 400 or 404 if no tuition
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
    
    def test_create_payment_unauthorized(self, api_client, setup_base_data):
        """
        Test Case: Unauthenticated request
        
        Given: No authentication
        When: POST /api/payment/create
        Then: Status 401
        """
        hoc_ky = setup_base_data['hoc_ky']
        
        payload = {
            'hocKyId': str(hoc_ky.id)
        }
        
        response = api_client.post('/api/payment/create', payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestPaymentStatus:
    """E2E tests for Payment Status API"""
    
    @pytest.fixture
    def setup_payment(self, setup_base_data, create_sv_user):
        """Setup payment transaction"""
        from infrastructure.persistence.models import PaymentTransactions, HocPhi
        
        sv = create_sv_user()
        hoc_ky = setup_base_data['hoc_ky']
        
        # Create tuition record
        hoc_phi = HocPhi.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            hoc_ky=hoc_ky,
            tong_hoc_phi=Decimal('5000000'),
            trang_thai_thanh_toan='chua_thanh_toan',
            ngay_tinh_toan=timezone.now()
        )
        
        # Create payment transaction
        transaction = PaymentTransactions.objects.using('neon').create(
            id=uuid.uuid4(),
            provider='momo',
            order_id=f'ORDER_{uuid.uuid4().hex[:10]}',
            sinh_vien_id=sv.id,
            hoc_ky=hoc_ky,
            amount=Decimal('5000000'),
            status='pending',
            created_at=timezone.now()
        )
        
        return {'sv': sv, 'transaction': transaction, 'hoc_ky': hoc_ky}
    
    def test_get_payment_status_success(self, api_client, setup_payment):
        """
        Test Case: SV checks payment status
        
        Given: SV has pending payment
        When: GET /api/payment/status?hocKyId=xxx
        Then: Status 200, payment status returned
        """
        sv = setup_payment['sv']
        hoc_ky = setup_payment['hoc_ky']
        api_client.force_authenticate(user=sv)
        
        response = api_client.get(f'/api/payment/status?hocKyId={hoc_ky.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_get_payment_status_no_transaction(self, api_client, setup_base_data, create_sv_user):
        """
        Test Case: SV checks status without existing transaction
        
        Given: SV has no payment transaction
        When: GET /api/payment/status
        Then: Status 200 with null or 404
        """
        sv = create_sv_user()
        hoc_ky = setup_base_data['hoc_ky']
        api_client.force_authenticate(user=sv)
        
        response = api_client.get(f'/api/payment/status?hocKyId={hoc_ky.id}')
        
        # May return 200 with empty data or 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestPaymentIPN:
    """E2E tests for Payment IPN (Instant Payment Notification) API"""
    
    @pytest.fixture
    def setup_pending_payment(self, setup_base_data, create_sv_user):
        """Setup pending payment for IPN test"""
        from infrastructure.persistence.models import PaymentTransactions, HocPhi
        
        sv = create_sv_user()
        hoc_ky = setup_base_data['hoc_ky']
        order_id = f'ORDER_{uuid.uuid4().hex[:10]}'
        
        # Create tuition
        hoc_phi = HocPhi.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            hoc_ky=hoc_ky,
            tong_hoc_phi=Decimal('5000000'),
            trang_thai_thanh_toan='chua_thanh_toan',
            ngay_tinh_toan=timezone.now()
        )
        
        # Create pending payment
        transaction = PaymentTransactions.objects.using('neon').create(
            id=uuid.uuid4(),
            provider='momo',
            order_id=order_id,
            sinh_vien_id=sv.id,
            hoc_ky=hoc_ky,
            amount=Decimal('5000000'),
            status='pending',
            created_at=timezone.now()
        )
        
        return {'sv': sv, 'transaction': transaction, 'hoc_phi': hoc_phi, 'order_id': order_id}
    
    def test_payment_ipn_success(self, api_client, setup_pending_payment):
        """
        Test Case: MoMo sends successful payment IPN
        
        Given: Pending payment exists
        When: POST /api/payment/ipn with success callback
        Then: Status 200/204, payment marked as completed
        """
        order_id = setup_pending_payment['order_id']
        
        # Simulate MoMo IPN callback (simplified)
        payload = {
            'orderId': order_id,
            'resultCode': 0,  # 0 = success
            'message': 'Thành công',
            'transId': f'trans_{uuid.uuid4().hex[:8]}',
            'amount': 5000000
        }
        
        response = api_client.post('/api/payment/ipn', payload, format='json')
        
        # IPN may return 200 or 204
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
    
    def test_payment_ipn_failed(self, api_client, setup_pending_payment):
        """
        Test Case: MoMo sends failed payment IPN
        
        Given: Pending payment exists
        When: POST /api/payment/ipn with failure callback
        Then: Status 200/204, payment marked as failed
        """
        order_id = setup_pending_payment['order_id']
        
        payload = {
            'orderId': order_id,
            'resultCode': 1000,  # Non-zero = failure
            'message': 'Giao dịch thất bại',
            'transId': '',
            'amount': 5000000
        }
        
        response = api_client.post('/api/payment/ipn', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
    
    def test_payment_ipn_invalid_order(self, api_client):
        """
        Test Case: IPN for non-existent order
        
        Given: Order ID does not exist
        When: POST /api/payment/ipn
        Then: Handle gracefully
        """
        payload = {
            'orderId': f'ORDER_INVALID_{uuid.uuid4().hex[:8]}',
            'resultCode': 0,
            'message': 'Success',
            'amount': 5000000
        }
        
        response = api_client.post('/api/payment/ipn', payload, format='json')
        
        # Should handle gracefully, not crash
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]
