"""
Unit Tests for Payment Use Cases
Tests: CreatePayment, GetPaymentStatus, ProcessIPN
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()

from application.payment.create_payment_use_case import CreatePaymentUseCase
from application.payment.get_payment_status_use_case import GetPaymentStatusUseCase
from application.payment.process_ipn_use_case import ProcessIPNUseCase


# ==================== Fixtures ====================

@pytest.fixture
def mock_payment_repo():
    """Mock payment repository"""
    repo = Mock()
    repo.create_transaction.return_value = True
    repo.update_status.return_value = True
    return repo


@pytest.fixture
def mock_hoc_phi_repo():
    """Mock hoc phi repository"""
    repo = Mock()
    repo.update_payment_status.return_value = True
    return repo


@pytest.fixture
def mock_hoc_phi():
    """Mock hoc phi object"""
    hoc_phi = Mock()
    hoc_phi.tong_hoc_phi = Decimal("15000000.0")
    hoc_phi.trang_thai_thanh_toan = "chua_thanh_toan"
    return hoc_phi


@pytest.fixture
def mock_transaction():
    """Mock payment transaction"""
    tx = Mock()
    tx.order_id = "ORDER123456"
    tx.amount = Decimal("15000000.0")
    tx.provider = "momo"
    tx.status = "pending"
    tx.sinh_vien_id = "sv-001"
    tx.hoc_ky_id = "hk-001"
    return tx


# ==================== CreatePaymentUseCase Tests ====================

class TestCreatePaymentUseCase:
    """Tests for CreatePaymentUseCase"""
    
    def test_create_payment_success(self, mock_payment_repo, mock_hoc_phi_repo, mock_hoc_phi):
        """Test successful payment creation"""
        # Arrange
        mock_hoc_phi_repo.get_hoc_phi_by_sinh_vien.return_value = mock_hoc_phi
        
        mock_gateway_response = MagicMock()
        mock_gateway_response.pay_url = "https://momo.vn/payment?orderId=ORDER123"
        mock_gateway_response.order_id = "ORDER123"
        
        # Patch at the infrastructure.gateways module level
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.create_payment.return_value = mock_gateway_response
            mock_factory.create.return_value = mock_gateway
            
            use_case = CreatePaymentUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("sv-001", "hk-001", "momo")
        
        # Assert
        assert result.success is True
        assert result.data["payUrl"] == "https://momo.vn/payment?orderId=ORDER123"
        assert result.data["orderId"] == "ORDER123"
        mock_payment_repo.create_transaction.assert_called_once()
    
    def test_create_payment_hoc_phi_not_found(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test payment creation when hoc_phi not found"""
        # Arrange
        mock_hoc_phi_repo.get_hoc_phi_by_sinh_vien.return_value = None
        use_case = CreatePaymentUseCase(mock_payment_repo, mock_hoc_phi_repo)
        
        # Act
        result = use_case.execute("sv-001", "hk-001", "momo")
        
        # Assert
        assert result.success is False
        assert result.error_code == "TUITION_NOT_FOUND"
        mock_payment_repo.create_transaction.assert_not_called()
    
    def test_create_payment_already_paid(self, mock_payment_repo, mock_hoc_phi_repo, mock_hoc_phi):
        """Test payment creation when already paid"""
        # Arrange
        mock_hoc_phi.trang_thai_thanh_toan = "da_thanh_toan"
        mock_hoc_phi_repo.get_hoc_phi_by_sinh_vien.return_value = mock_hoc_phi
        use_case = CreatePaymentUseCase(mock_payment_repo, mock_hoc_phi_repo)
        
        # Act
        result = use_case.execute("sv-001", "hk-001", "momo")
        
        # Assert
        assert result.success is False
        assert result.error_code == "ALREADY_PAID"
        mock_payment_repo.create_transaction.assert_not_called()
    
    def test_create_payment_invalid_amount(self, mock_payment_repo, mock_hoc_phi_repo, mock_hoc_phi):
        """Test payment creation with invalid amount"""
        # Arrange
        mock_hoc_phi.tong_hoc_phi = Decimal("0")
        mock_hoc_phi_repo.get_hoc_phi_by_sinh_vien.return_value = mock_hoc_phi
        use_case = CreatePaymentUseCase(mock_payment_repo, mock_hoc_phi_repo)
        
        # Act
        result = use_case.execute("sv-001", "hk-001", "momo")
        
        # Assert
        assert result.success is False
        assert result.error_code == "INVALID_AMOUNT"
    
    def test_create_payment_vnpay_provider(self, mock_payment_repo, mock_hoc_phi_repo, mock_hoc_phi):
        """Test payment creation with VNPay provider"""
        # Arrange
        mock_hoc_phi_repo.get_hoc_phi_by_sinh_vien.return_value = mock_hoc_phi
        
        mock_gateway_response = MagicMock()
        mock_gateway_response.pay_url = "https://vnpay.vn/payment?orderId=ORDER456"
        mock_gateway_response.order_id = "ORDER456"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.create_payment.return_value = mock_gateway_response
            mock_factory.create.return_value = mock_gateway
            
            use_case = CreatePaymentUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("sv-001", "hk-001", "vnpay")
        
        # Assert
        assert result.success is True
        mock_factory.create.assert_called_with("vnpay")
    
    def test_create_payment_exception(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test payment creation handles exceptions"""
        # Arrange
        mock_hoc_phi_repo.get_hoc_phi_by_sinh_vien.side_effect = Exception("Database error")
        use_case = CreatePaymentUseCase(mock_payment_repo, mock_hoc_phi_repo)
        
        # Act
        result = use_case.execute("sv-001", "hk-001", "momo")
        
        # Assert
        assert result.success is False
        assert result.error_code == "INTERNAL_ERROR"


# ==================== GetPaymentStatusUseCase Tests ====================

class TestGetPaymentStatusUseCase:
    """Tests for GetPaymentStatusUseCase"""
    
    def test_get_status_success(self, mock_payment_repo, mock_transaction):
        """Test successful status retrieval"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = mock_transaction
        use_case = GetPaymentStatusUseCase(mock_payment_repo)
        
        # Act
        result = use_case.execute("ORDER123456")
        
        # Assert
        assert result.success is True
        assert result.data["orderId"] == "ORDER123456"
        assert result.data["status"] == "pending"
        assert result.data["amount"] == 15000000.0
    
    def test_get_status_not_found(self, mock_payment_repo):
        """Test status retrieval when transaction not found"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = None
        use_case = GetPaymentStatusUseCase(mock_payment_repo)
        
        # Act
        result = use_case.execute("INVALID_ORDER")
        
        # Assert
        assert result.success is False
        assert result.error_code == "TRANSACTION_NOT_FOUND"
    
    def test_get_status_success_status(self, mock_payment_repo, mock_transaction):
        """Test status retrieval for successful payment"""
        # Arrange
        mock_transaction.status = "success"
        mock_payment_repo.get_by_order_id.return_value = mock_transaction
        use_case = GetPaymentStatusUseCase(mock_payment_repo)
        
        # Act
        result = use_case.execute("ORDER123456")
        
        # Assert
        assert result.success is True
        assert result.data["status"] == "success"
    
    def test_get_status_exception(self, mock_payment_repo):
        """Test status retrieval handles exceptions"""
        # Arrange
        mock_payment_repo.get_by_order_id.side_effect = Exception("DB connection error")
        use_case = GetPaymentStatusUseCase(mock_payment_repo)
        
        # Act
        result = use_case.execute("ORDER123456")
        
        # Assert
        assert result.success is False
        assert result.error_code == "INTERNAL_ERROR"


# ==================== ProcessIPNUseCase Tests ====================

class TestProcessIPNUseCase:
    """Tests for ProcessIPNUseCase"""
    
    def test_process_ipn_momo_success(self, mock_payment_repo, mock_hoc_phi_repo, mock_transaction):
        """Test processing successful MoMo IPN"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = mock_transaction
        
        mock_verify_result = MagicMock()
        mock_verify_result.is_valid = True
        mock_verify_result.order_id = "ORDER123456"
        mock_verify_result.result_code = "0"
        mock_verify_result.transaction_id = "TX123456"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.verify_ipn.return_value = mock_verify_result
            mock_factory.create.return_value = mock_gateway
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("momo", {"orderId": "ORDER123456", "resultCode": "0"})
        
        # Assert
        assert result.success is True
        assert result.data["status"] == "success"
        mock_payment_repo.update_status.assert_called_with("ORDER123456", "success")
        mock_hoc_phi_repo.update_payment_status.assert_called_with("sv-001", "hk-001", "da_thanh_toan")
    
    def test_process_ipn_vnpay_success(self, mock_payment_repo, mock_hoc_phi_repo, mock_transaction):
        """Test processing successful VNPay IPN"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = mock_transaction
        
        mock_verify_result = MagicMock()
        mock_verify_result.is_valid = True
        mock_verify_result.order_id = "ORDER123456"
        mock_verify_result.result_code = "00"
        mock_verify_result.transaction_id = "TX123456"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.verify_ipn.return_value = mock_verify_result
            mock_factory.create.return_value = mock_gateway
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("vnpay", {"vnp_ResponseCode": "00"})
        
        # Assert
        assert result.success is True
        assert result.data["status"] == "success"
    
    def test_process_ipn_zalopay_success(self, mock_payment_repo, mock_hoc_phi_repo, mock_transaction):
        """Test processing successful ZaloPay IPN"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = mock_transaction
        
        mock_verify_result = MagicMock()
        mock_verify_result.is_valid = True
        mock_verify_result.order_id = "ORDER123456"
        mock_verify_result.result_code = "1"
        mock_verify_result.transaction_id = "TX123456"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.verify_ipn.return_value = mock_verify_result
            mock_factory.create.return_value = mock_gateway
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("zalopay", {"data": "test"})
        
        # Assert
        assert result.success is True
        assert result.data["status"] == "success"
    
    def test_process_ipn_invalid_signature(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test processing IPN with invalid signature"""
        # Arrange
        mock_verify_result = MagicMock()
        mock_verify_result.is_valid = False
        mock_verify_result.order_id = "ORDER123456"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.verify_ipn.return_value = mock_verify_result
            mock_factory.create.return_value = mock_gateway
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("momo", {"orderId": "ORDER123456"})
        
        # Assert
        assert result.success is False
        assert result.error_code == "INVALID_SIGNATURE"
    
    def test_process_ipn_transaction_not_found(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test processing IPN when transaction not found"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = None
        
        mock_verify_result = MagicMock()
        mock_verify_result.is_valid = True
        mock_verify_result.order_id = "INVALID_ORDER"
        mock_verify_result.result_code = "0"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.verify_ipn.return_value = mock_verify_result
            mock_factory.create.return_value = mock_gateway
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("momo", {"orderId": "INVALID_ORDER"})
        
        # Assert
        assert result.success is False
        assert result.error_code == "TRANSACTION_NOT_FOUND"
    
    def test_process_ipn_payment_failed(self, mock_payment_repo, mock_hoc_phi_repo, mock_transaction):
        """Test processing IPN when payment failed"""
        # Arrange
        mock_payment_repo.get_by_order_id.return_value = mock_transaction
        
        mock_verify_result = MagicMock()
        mock_verify_result.is_valid = True
        mock_verify_result.order_id = "ORDER123456"
        mock_verify_result.result_code = "9999"  # Failed code
        mock_verify_result.transaction_id = "TX123456"
        
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_gateway = MagicMock()
            mock_gateway.verify_ipn.return_value = mock_verify_result
            mock_factory.create.return_value = mock_gateway
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("momo", {"orderId": "ORDER123456", "resultCode": "9999"})
        
        # Assert
        assert result.success is True
        assert result.data["status"] == "failed"
        mock_payment_repo.update_status.assert_called_with("ORDER123456", "failed")
    
    def test_process_ipn_exception(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test processing IPN handles exceptions"""
        # Arrange
        with patch("infrastructure.gateways.PaymentGatewayFactory") as mock_factory:
            mock_factory.create.side_effect = Exception("Gateway error")
            
            use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
            
            # Act
            result = use_case.execute("momo", {"orderId": "ORDER123456"})
        
        # Assert
        assert result.success is False
        assert result.error_code == "INTERNAL_ERROR"


# ==================== ProcessIPNUseCase Helper Method Tests ====================

class TestProcessIPNHelperMethods:
    """Tests for ProcessIPNUseCase helper methods"""
    
    def test_is_payment_successful_momo_success(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test MoMo success code detection"""
        use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
        assert use_case._is_payment_successful("momo", "0") is True
        assert use_case._is_payment_successful("momo", "1") is False
    
    def test_is_payment_successful_vnpay_success(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test VNPay success code detection"""
        use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
        assert use_case._is_payment_successful("vnpay", "00") is True
        assert use_case._is_payment_successful("vnpay", "01") is False
    
    def test_is_payment_successful_zalopay_success(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test ZaloPay success code detection"""
        use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
        assert use_case._is_payment_successful("zalopay", "1") is True
        assert use_case._is_payment_successful("zalopay", "0") is False
    
    def test_is_payment_successful_unknown_provider(self, mock_payment_repo, mock_hoc_phi_repo):
        """Test unknown provider returns False"""
        use_case = ProcessIPNUseCase(mock_payment_repo, mock_hoc_phi_repo)
        assert use_case._is_payment_successful("unknown", "0") is False
