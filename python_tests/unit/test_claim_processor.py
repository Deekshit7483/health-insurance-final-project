"""
Unit tests for claim processor module

These tests cover the main functionality of the ClaimProcessor,
Patient, Claim, and AuthenticationService classes.
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python_src.claim_processor import (
    ClaimProcessor, Patient, Claim, ClaimStatus, UserType,
    AuthenticationService, validate_insurance_id, format_currency,
    calculate_claim_processing_fee
)


class TestPatient:
    """Test cases for Patient class"""
    
    def test_patient_creation_valid(self):
        """Test creating a valid patient"""
        patient = Patient(
            id="P001",
            name="John Doe",
            email="john.doe@example.com",
            date_of_birth=date(1990, 1, 1),
            insurance_id="INS123456789",
            phone="555-123-4567"
        )
        
        assert patient.id == "P001"
        assert patient.name == "John Doe"
        assert patient.email == "john.doe@example.com"
        assert patient.insurance_id == "INS123456789"
        assert patient.phone == "555-123-4567"
    
    def test_patient_invalid_email(self):
        """Test patient creation with invalid email"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Patient(
                id="P001",
                name="John Doe",
                email="invalid-email",
                date_of_birth=date(1990, 1, 1),
                insurance_id="INS123456789"
            )
    
    def test_patient_empty_insurance_id(self):
        """Test patient creation with empty insurance ID"""
        with pytest.raises(ValueError, match="Insurance ID is required"):
            Patient(
                id="P001",
                name="John Doe",
                email="john.doe@example.com",
                date_of_birth=date(1990, 1, 1),
                insurance_id=""
            )


class TestClaim:
    """Test cases for Claim class"""
    
    def test_claim_creation_valid(self):
        """Test creating a valid claim"""
        claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=150.50,
            description="Annual checkup",
            date_of_service=date(2024, 1, 15)
        )
        
        assert claim.id == "C001"
        assert claim.patient_id == "P001"
        assert claim.amount == 150.50
        assert claim.status == ClaimStatus.PENDING
        assert claim.created_at is not None
        assert claim.updated_at is not None
    
    def test_claim_negative_amount(self):
        """Test claim creation with negative amount"""
        with pytest.raises(ValueError, match="Claim amount must be positive"):
            Claim(
                id="C001",
                patient_id="P001",
                provider_id="PR001",
                amount=-50.0,
                description="Invalid claim",
                date_of_service=date(2024, 1, 15)
            )
    
    def test_claim_short_description(self):
        """Test claim creation with short description"""
        with pytest.raises(ValueError, match="Claim description must be at least 5 characters"):
            Claim(
                id="C001",
                patient_id="P001",
                provider_id="PR001",
                amount=100.0,
                description="abc",
                date_of_service=date(2024, 1, 15)
            )


class TestClaimProcessor:
    """Test cases for ClaimProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Fixture to provide a fresh ClaimProcessor instance"""
        return ClaimProcessor()
    
    @pytest.fixture
    def sample_patient(self):
        """Fixture to provide a sample patient"""
        return Patient(
            id="P001",
            name="John Doe",
            email="john.doe@example.com",
            date_of_birth=date(1990, 1, 1),
            insurance_id="INS123456789"
        )
    
    @pytest.fixture
    def sample_claim(self):
        """Fixture to provide a sample claim"""
        return Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=150.50,
            description="Annual checkup",
            date_of_service=date(2024, 1, 15)
        )
    
    def test_register_patient_success(self, processor, sample_patient):
        """Test successful patient registration"""
        result = processor.register_patient(sample_patient)
        
        assert result is True
        assert processor.get_patient("P001") == sample_patient
    
    def test_register_patient_duplicate(self, processor, sample_patient):
        """Test registering duplicate patient"""
        processor.register_patient(sample_patient)
        result = processor.register_patient(sample_patient)
        
        assert result is False
    
    def test_submit_claim_success(self, processor, sample_patient, sample_claim):
        """Test successful claim submission"""
        processor.register_patient(sample_patient)
        result = processor.submit_claim(sample_claim)
        
        assert result is True
        assert processor.get_claim("C001") == sample_claim
    
    def test_submit_claim_patient_not_found(self, processor, sample_claim):
        """Test claim submission for non-existent patient"""
        with pytest.raises(ValueError, match="Patient not found"):
            processor.submit_claim(sample_claim)
    
    def test_submit_claim_exceeds_limit(self, processor, sample_patient):
        """Test claim submission that exceeds maximum limit"""
        processor.register_patient(sample_patient)
        
        large_claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=60000.0,  # Exceeds max_claim_amount of 50000
            description="Large medical procedure",
            date_of_service=date(2024, 1, 15)
        )
        
        with pytest.raises(ValueError, match="Claim amount exceeds maximum limit"):
            processor.submit_claim(large_claim)
    
    def test_auto_approve_small_claim(self, processor, sample_patient):
        """Test automatic approval of small claims"""
        processor.register_patient(sample_patient)
        
        small_claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=50.0,  # Below auto_approve_threshold of 100
            description="Small procedure",
            date_of_service=date(2024, 1, 15)
        )
        
        processor.submit_claim(small_claim)
        
        assert small_claim.status == ClaimStatus.APPROVED
    
    def test_large_claim_requires_review(self, processor, sample_patient):
        """Test that large claims require review"""
        processor.register_patient(sample_patient)
        
        large_claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=15000.0,  # Above 10000 threshold
            description="Major surgery",
            date_of_service=date(2024, 1, 15)
        )
        
        processor.submit_claim(large_claim)
        
        assert large_claim.status == ClaimStatus.REQUIRES_REVIEW
    
    def test_approve_claim_success(self, processor, sample_patient, sample_claim):
        """Test manual claim approval"""
        processor.register_patient(sample_patient)
        processor.submit_claim(sample_claim)
        
        result = processor.approve_claim("C001")
        
        assert result is True
        assert sample_claim.status == ClaimStatus.APPROVED
    
    def test_approve_nonexistent_claim(self, processor):
        """Test approving non-existent claim"""
        result = processor.approve_claim("NONEXISTENT")
        
        assert result is False
    
    def test_approve_already_approved_claim(self, processor, sample_patient, sample_claim):
        """Test approving already approved claim"""
        processor.register_patient(sample_patient)
        processor.submit_claim(sample_claim)
        processor.approve_claim("C001")
        
        result = processor.approve_claim("C001")  # Try to approve again
        
        assert result is False
    
    def test_reject_claim_success(self, processor, sample_patient, sample_claim):
        """Test claim rejection"""
        processor.register_patient(sample_patient)
        processor.submit_claim(sample_claim)
        
        result = processor.reject_claim("C001", "Insufficient documentation")
        
        assert result is True
        assert sample_claim.status == ClaimStatus.REJECTED
    
    def test_get_claims_by_patient(self, processor, sample_patient):
        """Test retrieving claims by patient"""
        processor.register_patient(sample_patient)
        
        claim1 = Claim("C001", "P001", "PR001", 100.0, "Checkup 1", date(2024, 1, 1))
        claim2 = Claim("C002", "P001", "PR002", 200.0, "Checkup 2", date(2024, 1, 2))
        
        processor.submit_claim(claim1)
        processor.submit_claim(claim2)
        
        claims = processor.get_claims_by_patient("P001")
        
        assert len(claims) == 2
        assert claim1 in claims
        assert claim2 in claims
    
    def test_get_claims_by_status(self, processor, sample_patient):
        """Test retrieving claims by status"""
        processor.register_patient(sample_patient)
        
        # Create claims that will auto-approve
        claim1 = Claim("C001", "P001", "PR001", 50.0, "Small procedure 1", date(2024, 1, 1))
        claim2 = Claim("C002", "P001", "PR002", 60.0, "Small procedure 2", date(2024, 1, 2))
        
        processor.submit_claim(claim1)
        processor.submit_claim(claim2)
        
        approved_claims = processor.get_claims_by_status(ClaimStatus.APPROVED)
        
        assert len(approved_claims) == 2
    
    def test_calculate_total_approved_amount(self, processor, sample_patient):
        """Test calculating total approved amount for patient"""
        processor.register_patient(sample_patient)
        
        # Create small claims that will auto-approve
        claim1 = Claim("C001", "P001", "PR001", 50.0, "Procedure 1", date(2024, 1, 1))
        claim2 = Claim("C002", "P001", "PR002", 75.0, "Procedure 2", date(2024, 1, 2))
        
        processor.submit_claim(claim1)
        processor.submit_claim(claim2)
        
        total = processor.calculate_total_approved_amount("P001")
        
        assert total == 125.0


class TestAuthenticationService:
    """Test cases for AuthenticationService class"""
    
    @pytest.fixture
    def auth_service(self):
        """Fixture to provide a fresh AuthenticationService instance"""
        return AuthenticationService()
    
    def test_register_user_success(self, auth_service):
        """Test successful user registration"""
        result = auth_service.register_user(
            "U001", 
            "user@example.com", 
            "password123", 
            UserType.PATIENT
        )
        
        assert result is True
        assert "U001" in auth_service.users
    
    def test_register_user_duplicate(self, auth_service):
        """Test registering duplicate user"""
        auth_service.register_user("U001", "user@example.com", "password123", UserType.PATIENT)
        result = auth_service.register_user("U001", "user2@example.com", "password456", UserType.PROVIDER)
        
        assert result is False
    
    def test_register_user_invalid_email(self, auth_service):
        """Test user registration with invalid email"""
        with pytest.raises(ValueError, match="Invalid email format"):
            auth_service.register_user("U001", "invalid-email", "password123", UserType.PATIENT)
    
    def test_register_user_short_password(self, auth_service):
        """Test user registration with short password"""
        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            auth_service.register_user("U001", "user@example.com", "short", UserType.PATIENT)
    
    def test_authenticate_success(self, auth_service):
        """Test successful authentication"""
        auth_service.register_user("U001", "user@example.com", "password123", UserType.PATIENT)
        
        result = auth_service.authenticate("user@example.com", "password123")
        
        assert result is not None
        assert result['user_id'] == "U001"
        assert result['email'] == "user@example.com"
        assert result['user_type'] == UserType.PATIENT
    
    def test_authenticate_invalid_credentials(self, auth_service):
        """Test authentication with invalid credentials"""
        auth_service.register_user("U001", "user@example.com", "password123", UserType.PATIENT)
        
        result = auth_service.authenticate("user@example.com", "wrongpassword")
        
        assert result is None
    
    def test_create_and_validate_session(self, auth_service):
        """Test session creation and validation"""
        auth_service.register_user("U001", "user@example.com", "password123", UserType.PATIENT)
        
        token = auth_service.create_session("U001")
        user_id = auth_service.validate_session(token)
        
        assert token is not None
        assert len(token) > 0
        assert user_id == "U001"
    
    def test_logout(self, auth_service):
        """Test user logout"""
        auth_service.register_user("U001", "user@example.com", "password123", UserType.PATIENT)
        
        token = auth_service.create_session("U001")
        result = auth_service.logout(token)
        
        assert result is True
        assert auth_service.validate_session(token) is None


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_validate_insurance_id_valid(self):
        """Test valid insurance ID validation"""
        assert validate_insurance_id("ABC123456789") is True
        assert validate_insurance_id("12345678") is True
        assert validate_insurance_id("ABCD123456") is True
    
    def test_validate_insurance_id_invalid(self):
        """Test invalid insurance ID validation"""
        assert validate_insurance_id("") is False
        assert validate_insurance_id("abc123") is False  # Too short
        assert validate_insurance_id("ABCD1234567890") is False  # Too long
        assert validate_insurance_id("ABC-123456") is False  # Contains hyphen
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(100.0) == "$100.00"
        assert format_currency(0.99) == "$0.99"
        assert format_currency(1000000.50) == "$1,000,000.50"
    
    def test_calculate_claim_processing_fee(self):
        """Test claim processing fee calculation"""
        assert calculate_claim_processing_fee(500.0) == 25.0
        assert calculate_claim_processing_fee(3000.0) == 50.0
        assert calculate_claim_processing_fee(10000.0) == 100.0
        assert calculate_claim_processing_fee(1000.0) == 25.0  # Boundary case
        assert calculate_claim_processing_fee(5000.0) == 50.0  # Boundary case


# Integration test example
class TestClaimProcessorIntegration:
    """Integration tests for claim processor workflow"""
    
    def test_complete_claim_workflow(self):
        """Test complete workflow from patient registration to claim processing"""
        processor = ClaimProcessor()
        
        # Step 1: Register patient
        patient = Patient(
            id="P001",
            name="Jane Smith",
            email="jane.smith@example.com",
            date_of_birth=date(1985, 5, 15),
            insurance_id="INS987654321"
        )
        assert processor.register_patient(patient) is True
        
        # Step 2: Submit claim
        claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=250.0,  # Medium amount, should go to PROCESSING
            description="Routine blood work",
            date_of_service=date(2024, 1, 20)
        )
        assert processor.submit_claim(claim) is True
        assert claim.status == ClaimStatus.PROCESSING
        
        # Step 3: Manually approve claim
        assert processor.approve_claim("C001") is True
        assert claim.status == ClaimStatus.APPROVED
        
        # Step 4: Verify total approved amount
        total = processor.calculate_total_approved_amount("P001")
        assert total == 250.0
        
        # Step 5: Verify patient's claims
        patient_claims = processor.get_claims_by_patient("P001")
        assert len(patient_claims) == 1
        assert patient_claims[0] == claim