"""
Unit Tests for TaiLieu (Documents) Use Cases
Tests: GetTaiLieuByLHP, UploadTaiLieu, DeleteTaiLieu, UpdateTaiLieu
"""
import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
from typing import Optional
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()

from application.tai_lieu.use_cases.get_tai_lieu_by_lhp_use_case import GetTaiLieuByLHPUseCase
from application.tai_lieu.use_cases.upload_tai_lieu_use_case import UploadTaiLieuUseCase
from application.tai_lieu.use_cases.delete_tai_lieu_use_case import DeleteTaiLieuUseCase
from application.tai_lieu.use_cases.update_tai_lieu_use_case import UpdateTaiLieuUseCase


# ==================== GetTaiLieuByLHPUseCase Tests ====================

class TestGetTaiLieuByLHPUseCase:
    """Tests for GetTaiLieuByLHPUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_repo):
        return GetTaiLieuByLHPUseCase(mock_repo)
    
    def test_execute_success_returns_list(self, use_case, mock_repo):
        """
        Given: LHP has documents and GV owns it
        When: GetTaiLieuByLHPUseCase.execute() is called
        Then: Return ServiceResult with list of documents
        """
        # Arrange
        lhp_id = "lhp-001"
        gv_user_id = "gv-001"
        
        mock_repo.get_lop_hoc_phan_owner.return_value = gv_user_id
        
        mock_doc = MagicMock()
        mock_doc.id = "doc-001"
        mock_doc.ten_tai_lieu = "Bài giảng 1"
        mock_doc.file_path = "s3://bucket/doc1.pdf"
        mock_doc.file_type = "pdf"
        mock_doc.created_at = "2025-01-01"
        
        mock_repo.find_by_lop_hoc_phan.return_value = [mock_doc]
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is True
        assert isinstance(result.data, list)
        assert len(result.data) == 1
        assert result.data[0]["ten_tai_lieu"] == "Bài giảng 1"
    
    def test_execute_empty_list_when_no_docs(self, use_case, mock_repo):
        """
        Given: LHP has no documents
        When: GetTaiLieuByLHPUseCase.execute() is called
        Then: Return empty list
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        mock_repo.find_by_lop_hoc_phan.return_value = []
        
        result = use_case.execute("lhp-001", "gv-001")
        
        assert result.success is True
        assert result.data == []
    
    def test_execute_forbidden_when_gv_not_owner(self, use_case, mock_repo):
        """
        Given: GV is not the owner of LHP
        When: GetTaiLieuByLHPUseCase.execute() is called
        Then: Return forbidden
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-other"
        
        result = use_case.execute("lhp-001", "gv-001")
        
        assert result.success is False
        assert result.error_code == "FORBIDDEN"
    
    def test_execute_lhp_not_found(self, use_case, mock_repo):
        """
        Given: LHP does not exist
        When: GetTaiLieuByLHPUseCase.execute() is called
        Then: Return not found
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = None
        
        result = use_case.execute("lhp-invalid", "gv-001")
        
        assert result.success is False
        assert result.error_code == "LHP_NOT_FOUND"


# ==================== UploadTaiLieuUseCase Tests ====================

class TestUploadTaiLieuUseCase:
    """Tests for UploadTaiLieuUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_s3(self):
        s3 = Mock()
        s3.is_available = True
        return s3
    
    @pytest.fixture
    def use_case(self, mock_repo, mock_s3):
        return UploadTaiLieuUseCase(mock_repo, mock_s3)
    
    def test_execute_success(self, use_case, mock_repo, mock_s3):
        """
        Given: Valid file, GV owns LHP, S3 available
        When: UploadTaiLieuUseCase.execute() is called
        Then: Return success with new document
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        mock_s3.upload_file.return_value = {"key": "tai_lieu/lhp-001/new.pdf"}
        
        mock_created = MagicMock()
        mock_created.id = "doc-new"
        mock_created.ten_tai_lieu = "New Doc"
        mock_created.file_path = "tai_lieu/lhp-001/new.pdf"
        mock_created.file_type = "pdf"
        mock_repo.create.return_value = mock_created
        
        mock_file = MagicMock()
        
        result = use_case.execute(
            lhp_id="lhp-001",
            gv_user_id="gv-001",
            file_obj=mock_file,
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024,
            ten_tai_lieu="New Doc"
        )
        
        assert result.success is True
    
    def test_execute_forbidden_when_gv_not_owner(self, use_case, mock_repo, mock_s3):
        """
        Given: GV not owner of LHP
        When: UploadTaiLieuUseCase.execute() is called
        Then: Return forbidden
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-other"
        
        mock_file = MagicMock()
        
        result = use_case.execute(
            lhp_id="lhp-001",
            gv_user_id="gv-001",
            file_obj=mock_file,
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024
        )
        
        assert result.success is False
        assert result.error_code == "FORBIDDEN"
    
    def test_execute_file_too_large(self, use_case, mock_repo, mock_s3):
        """
        Given: File exceeds max size
        When: UploadTaiLieuUseCase.execute() is called
        Then: Return error
        """
        mock_file = MagicMock()
        
        result = use_case.execute(
            lhp_id="lhp-001",
            gv_user_id="gv-001",
            file_obj=mock_file,
            filename="test.pdf",
            content_type="application/pdf",
            file_size=200 * 1024 * 1024  # 200MB > 100MB limit
        )
        
        assert result.success is False
        assert result.error_code == "FILE_TOO_LARGE"
    
    def test_execute_s3_unavailable(self, use_case, mock_repo, mock_s3):
        """
        Given: S3 service unavailable
        When: UploadTaiLieuUseCase.execute() is called
        Then: Return error
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        mock_s3.is_available = False
        
        mock_file = MagicMock()
        
        result = use_case.execute(
            lhp_id="lhp-001",
            gv_user_id="gv-001",
            file_obj=mock_file,
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024
        )
        
        assert result.success is False
        assert result.error_code == "S3_UNAVAILABLE"


# ==================== DeleteTaiLieuUseCase Tests ====================

class TestDeleteTaiLieuUseCase:
    """Tests for DeleteTaiLieuUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_s3(self):
        s3 = Mock()
        s3.is_available = True
        return s3
    
    @pytest.fixture
    def use_case(self, mock_repo, mock_s3):
        return DeleteTaiLieuUseCase(mock_repo, mock_s3)
    
    def test_execute_success(self, use_case, mock_repo, mock_s3):
        """
        Given: Valid document, GV owns LHP
        When: DeleteTaiLieuUseCase.execute() is called
        Then: Return success
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        
        mock_doc = MagicMock()
        mock_doc.file_path = "s3://bucket/doc1.pdf"
        mock_repo.find_by_id.return_value = mock_doc
        mock_repo.delete.return_value = True
        
        result = use_case.execute("lhp-001", "doc-001", "gv-001")
        
        assert result.success is True
        mock_s3.delete_file.assert_called_once()
    
    def test_execute_not_found(self, use_case, mock_repo, mock_s3):
        """
        Given: Document not found
        When: DeleteTaiLieuUseCase.execute() is called
        Then: Return not found
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        mock_repo.find_by_id.return_value = None
        
        result = use_case.execute("lhp-001", "doc-not-exist", "gv-001")
        
        assert result.success is False
        assert result.error_code == "DOCUMENT_NOT_FOUND"
    
    def test_execute_forbidden(self, use_case, mock_repo, mock_s3):
        """
        Given: GV not owner of LHP
        When: DeleteTaiLieuUseCase.execute() is called
        Then: Return forbidden
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-other"
        
        result = use_case.execute("lhp-001", "doc-001", "gv-001")
        
        assert result.success is False
        assert result.error_code == "FORBIDDEN"


# ==================== UpdateTaiLieuUseCase Tests ====================

class TestUpdateTaiLieuUseCase:
    """Tests for UpdateTaiLieuUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_repo):
        return UpdateTaiLieuUseCase(mock_repo)
    
    def test_execute_success(self, use_case, mock_repo):
        """
        Given: Valid document, GV owns LHP
        When: UpdateTaiLieuUseCase.execute() is called
        Then: Return success with updated document
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        
        mock_doc = MagicMock()
        mock_doc.id = "doc-001"
        mock_repo.find_by_id.return_value = mock_doc
        
        mock_updated = MagicMock()
        mock_updated.id = "doc-001"
        mock_updated.ten_tai_lieu = "Updated Name"
        mock_updated.file_path = "s3://bucket/doc1.pdf"
        mock_repo.update_name.return_value = mock_updated
        
        result = use_case.execute("lhp-001", "doc-001", "gv-001", "Updated Name")
        
        assert result.success is True
        assert result.data["ten_tai_lieu"] == "Updated Name"
    
    def test_execute_not_found(self, use_case, mock_repo):
        """
        Given: Document not found
        When: UpdateTaiLieuUseCase.execute() is called
        Then: Return not found
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-001"
        mock_repo.find_by_id.return_value = None
        
        result = use_case.execute("lhp-001", "doc-not-exist", "gv-001", "New Name")
        
        assert result.success is False
        assert result.error_code == "DOCUMENT_NOT_FOUND"
    
    def test_execute_forbidden(self, use_case, mock_repo):
        """
        Given: GV not owner of LHP
        When: UpdateTaiLieuUseCase.execute() is called
        Then: Return forbidden
        """
        mock_repo.get_lop_hoc_phan_owner.return_value = "gv-other"
        
        result = use_case.execute("lhp-001", "doc-001", "gv-001", "New Name")
        
        assert result.success is False
        assert result.error_code == "FORBIDDEN"
    
    def test_execute_invalid_name(self, use_case, mock_repo):
        """
        Given: Empty name
        When: UpdateTaiLieuUseCase.execute() is called
        Then: Return validation error
        """
        result = use_case.execute("lhp-001", "doc-001", "gv-001", "")
        
        assert result.success is False
        assert result.error_code == "INVALID_NAME"
    
    def test_execute_whitespace_name(self, use_case, mock_repo):
        """
        Given: Whitespace-only name
        When: UpdateTaiLieuUseCase.execute() is called
        Then: Return validation error
        """
        result = use_case.execute("lhp-001", "doc-001", "gv-001", "   ")
        
        assert result.success is False
        assert result.error_code == "INVALID_NAME"
