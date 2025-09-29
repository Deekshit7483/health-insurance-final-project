"""
Integration tests for health insurance claim system

These tests cover end-to-end workflows combining multiple components.
"""

import pytest
import tempfile
import os
from datetime import date, datetime
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python_src.claim_processor import (
    ClaimProcessor, Patient, Claim, ClaimStatus, UserType,
    AuthenticationService
)
from python_src.database import DatabaseManager, DataValidator


class TestHealthInsuranceSystem:
    """Integration tests for the complete health insurance system"""
    
    @pytest.fixture
    def system_components(self):
        """Fixture to provide all system components"""
        claim_processor = ClaimProcessor()
        auth_service = AuthenticationService()
        db_manager = DatabaseManager(":memory:")
        
        return {
            'claim_processor': claim_processor,
            'auth_service': auth_service,
            'db_manager': db_manager
        }
    
    def test_complete_patient_registration_and_claim_flow(self, system_components):
        """Test complete flow from user registration to claim processing"""
        claim_processor = system_components['claim_processor']
        auth_service = system_components['auth_service']
        db_manager = system_components['db_manager']
        
        # Step 1: Register user in authentication system
        user_registered = auth_service.register_user(
            user_id="U001",
            email="patient@example.com",
            password="securepassword123",
            user_type=UserType.PATIENT
        )
        assert user_registered is True
        
        # Step 2: Authenticate user
        auth_result = auth_service.authenticate("patient@example.com", "securepassword123")
        assert auth_result is not None
        assert auth_result['user_type'] == UserType.PATIENT
        
        # Step 3: Create session
        session_token = auth_service.create_session("U001")
        assert session_token is not None
        
        # Step 4: Validate session
        user_id = auth_service.validate_session(session_token)
        assert user_id == "U001"
        
        # Step 5: Register patient in claim processor
        patient = Patient(
            id="P001",
            name="John Smith",
            email="patient@example.com",
            date_of_birth=date(1985, 6, 15),
            insurance_id="INS789012345",
            phone="555-234-5678"
        )
        
        patient_registered = claim_processor.register_patient(patient)
        assert patient_registered is True
        
        # Step 6: Store patient in database
        patient_data = {
            'id': patient.id,
            'name': patient.name,
            'email': patient.email,
            'date_of_birth': patient.date_of_birth.isoformat(),
            'insurance_id': patient.insurance_id,
            'phone': patient.phone
        }
        
        db_patient_stored = db_manager.insert_patient(patient_data)
        assert db_patient_stored is True
        
        # Step 7: Submit multiple claims
        claims = [
            Claim(
                id="C001",
                patient_id="P001",
                provider_id="PR001",
                amount=75.0,  # Small amount - should auto-approve
                description="Routine blood pressure check",
                date_of_service=date(2024, 1, 10)
            ),
            Claim(
                id="C002",
                patient_id="P001",
                provider_id="PR002",
                amount=500.0,  # Medium amount - should go to processing
                description="Annual physical examination",
                date_of_service=date(2024, 1, 15)
            ),
            Claim(
                id="C003",
                patient_id="P001",
                provider_id="PR003",
                amount=15000.0,  # Large amount - should require review
                description="Emergency surgery consultation",
                date_of_service=date(2024, 1, 20)
            )
        ]
        
        for claim in claims:
            claim_submitted = claim_processor.submit_claim(claim)
            assert claim_submitted is True
            
            # Store claim in database
            claim_data = {
                'id': claim.id,
                'patient_id': claim.patient_id,
                'provider_id': claim.provider_id,
                'amount': claim.amount,
                'description': claim.description,
                'date_of_service': claim.date_of_service.isoformat(),
                'status': claim.status.value
            }
            
            db_claim_stored = db_manager.insert_claim(claim_data)
            assert db_claim_stored is True
        
        # Step 8: Verify automatic processing results
        claim1 = claim_processor.get_claim("C001")
        claim2 = claim_processor.get_claim("C002")
        claim3 = claim_processor.get_claim("C003")
        
        assert claim1.status == ClaimStatus.APPROVED  # Auto-approved (small amount)
        assert claim2.status == ClaimStatus.PROCESSING  # Medium amount
        assert claim3.status == ClaimStatus.REQUIRES_REVIEW  # Large amount
        
        # Step 9: Manually process remaining claims
        # Approve the medium claim
        approval_result = claim_processor.approve_claim("C002")
        assert approval_result is True
        db_manager.update_claim_status("C002", "approved")
        
        # Reject the large claim (insufficient documentation)
        rejection_result = claim_processor.reject_claim("C003", "Insufficient documentation")
        assert rejection_result is True
        db_manager.update_claim_status("C003", "rejected")
        
        # Step 10: Verify final states
        final_claim2 = claim_processor.get_claim("C002")
        final_claim3 = claim_processor.get_claim("C003")
        
        assert final_claim2.status == ClaimStatus.APPROVED
        assert final_claim3.status == ClaimStatus.REJECTED
        
        # Step 11: Calculate total approved amount
        total_approved = claim_processor.calculate_total_approved_amount("P001")
        assert total_approved == 575.0  # 75.0 + 500.0
        
        # Step 12: Verify database consistency
        db_patient_claims = db_manager.get_claims_by_patient("P001")
        assert len(db_patient_claims) == 3
        
        db_approved_claims = db_manager.get_claims_by_status("approved")
        assert len(db_approved_claims) == 2
        
        db_rejected_claims = db_manager.get_claims_by_status("rejected")
        assert len(db_rejected_claims) == 1
        
        # Step 13: Check statistics
        stats = db_manager.get_claim_statistics()
        assert stats['total_claims'] == 3
        assert stats['status_breakdown']['approved']['count'] == 2
        assert stats['status_breakdown']['rejected']['count'] == 1
        
        # Step 14: Logout user
        logout_result = auth_service.logout(session_token)
        assert logout_result is True
        
        # Verify session is invalid
        invalid_user = auth_service.validate_session(session_token)
        assert invalid_user is None
    
    def test_multi_user_workflow(self, system_components):
        """Test workflow with multiple users (patient, provider, payor)"""
        auth_service = system_components['auth_service']
        claim_processor = system_components['claim_processor']
        db_manager = system_components['db_manager']
        
        # Register different types of users
        users = [
            ("U001", "patient@example.com", "password123", UserType.PATIENT),
            ("U002", "provider@hospital.com", "password456", UserType.PROVIDER),
            ("U003", "payor@insurance.com", "password789", UserType.PAYOR)
        ]
        
        sessions = {}
        
        for user_id, email, password, user_type in users:
            # Register user
            registered = auth_service.register_user(user_id, email, password, user_type)
            assert registered is True
            
            # Authenticate and create session
            auth_result = auth_service.authenticate(email, password)
            assert auth_result is not None
            assert auth_result['user_type'] == user_type
            
            session_token = auth_service.create_session(user_id)
            sessions[user_type] = session_token
        
        # Patient workflow
        patient = Patient(
            id="P001",
            name="Mary Johnson",
            email="patient@example.com",
            date_of_birth=date(1992, 8, 25),
            insurance_id="INS456789012"
        )
        
        claim_processor.register_patient(patient)
        
        # Provider workflow - submit claim on behalf of patient
        provider_claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=1200.0,
            description="Specialist consultation and diagnostic tests",
            date_of_service=date(2024, 2, 1)
        )
        
        claim_processor.submit_claim(provider_claim)
        assert provider_claim.status == ClaimStatus.PROCESSING
        
        # Payor workflow - review and approve claim
        payor_approval = claim_processor.approve_claim("C001")
        assert payor_approval is True
        
        # Verify all sessions are still valid
        for user_type, token in sessions.items():
            user_id = auth_service.validate_session(token)
            assert user_id is not None
        
        # Logout all users
        for user_type, token in sessions.items():
            logout_result = auth_service.logout(token)
            assert logout_result is True
    
    def test_data_validation_integration(self, system_components):
        """Test integration of data validation across components"""
        claim_processor = system_components['claim_processor']
        db_manager = system_components['db_manager']
        
        # Test invalid patient data
        with pytest.raises(ValueError, match="Invalid email format"):
            Patient(
                id="P001",
                name="Invalid Patient",
                email="invalid-email",
                date_of_birth=date(1990, 1, 1),
                insurance_id="INS123456789"
            )
        
        # Test valid patient with database validation
        patient = Patient(
            id="P001",
            name="Valid Patient",
            email="valid@example.com",
            date_of_birth=date(1990, 1, 1),
            insurance_id="INS123456789",
            phone="555-123-4567"
        )
        
        # Validate email using DataValidator
        assert DataValidator.validate_email(patient.email) is True
        assert DataValidator.validate_phone(patient.phone) is True
        
        claim_processor.register_patient(patient)
        
        # Test invalid claim data
        with pytest.raises(ValueError, match="Claim amount must be positive"):
            Claim(
                id="C001",
                patient_id="P001",
                provider_id="PR001",
                amount=-100.0,
                description="Invalid negative amount",
                date_of_service=date(2024, 1, 1)
            )
        
        # Test valid claim with amount validation
        valid_claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=250.0,
            description="Valid medical service",
            date_of_service=date(2024, 1, 1)
        )
        
        # Validate amount using DataValidator
        assert DataValidator.validate_amount(valid_claim.amount) is True
        
        claim_processor.submit_claim(valid_claim)
        
        # Test date range validation
        service_date = date(2024, 1, 1)
        current_date = date(2024, 1, 15)
        
        assert DataValidator.validate_date_range(service_date, current_date) is True
    
    def test_error_handling_integration(self, system_components):
        """Test error handling across integrated components"""
        claim_processor = system_components['claim_processor']
        auth_service = system_components['auth_service']
        db_manager = system_components['db_manager']
        
        # Test claim submission without registered patient
        claim = Claim(
            id="C001",
            patient_id="NONEXISTENT",
            provider_id="PR001",
            amount=100.0,
            description="Claim for non-existent patient",
            date_of_service=date(2024, 1, 1)
        )
        
        with pytest.raises(ValueError, match="Patient not found"):
            claim_processor.submit_claim(claim)
        
        # Test claim amount exceeding limit
        patient = Patient(
            id="P001",
            name="Test Patient",
            email="test@example.com",
            date_of_birth=date(1990, 1, 1),
            insurance_id="INS123456789"
        )
        
        claim_processor.register_patient(patient)
        
        large_claim = Claim(
            id="C001",
            patient_id="P001",
            provider_id="PR001",
            amount=60000.0,  # Exceeds max_claim_amount
            description="Claim exceeding limit",
            date_of_service=date(2024, 1, 1)
        )
        
        with pytest.raises(ValueError, match="Claim amount exceeds maximum limit"):
            claim_processor.submit_claim(large_claim)
        
        # Test duplicate user registration
        auth_service.register_user("U001", "user@example.com", "password123", UserType.PATIENT)
        
        duplicate_result = auth_service.register_user("U001", "other@example.com", "password456", UserType.PROVIDER)
        assert duplicate_result is False
        
        # Test authentication with invalid credentials
        auth_result = auth_service.authenticate("user@example.com", "wrongpassword")
        assert auth_result is None
        
        # Test database operations with invalid data
        invalid_patient_data = {
            'id': 'P001',
            'name': 'Duplicate Patient',
            'email': 'test@example.com',  # Same email as existing patient
            'date_of_birth': '1990-01-01',
            'insurance_id': 'INS987654321'
        }
        
        # First insert should succeed
        patient_data = {
            'id': 'P001',
            'name': 'Original Patient',
            'email': 'test@example.com',
            'date_of_birth': '1990-01-01',
            'insurance_id': 'INS123456789'
        }
        
        first_insert = db_manager.insert_patient(patient_data)
        assert first_insert is True
        
        # Second insert with duplicate email should fail
        second_insert = db_manager.insert_patient(invalid_patient_data)
        assert second_insert is False
    
    def test_performance_with_multiple_claims(self, system_components):
        """Test system performance with multiple claims"""
        claim_processor = system_components['claim_processor']
        db_manager = system_components['db_manager']
        
        # Register multiple patients
        patients = []
        for i in range(10):
            patient = Patient(
                id=f"P{i:03d}",
                name=f"Patient {i}",
                email=f"patient{i}@example.com",
                date_of_birth=date(1990, 1, 1),
                insurance_id=f"INS{i:09d}"
            )
            
            claim_processor.register_patient(patient)
            patients.append(patient)
            
            # Store in database
            patient_data = {
                'id': patient.id,
                'name': patient.name,
                'email': patient.email,
                'date_of_birth': patient.date_of_birth.isoformat(),
                'insurance_id': patient.insurance_id,
                'phone': None
            }
            db_manager.insert_patient(patient_data)
        
        # Submit multiple claims for each patient
        total_claims = 0
        for i, patient in enumerate(patients):
            for j in range(5):  # 5 claims per patient
                claim = Claim(
                    id=f"C{i:03d}_{j:03d}",
                    patient_id=patient.id,
                    provider_id=f"PR{j:03d}",
                    amount=100.0 + (j * 50.0),
                    description=f"Medical service {j} for patient {i}",
                    date_of_service=date(2024, 1, j + 1)
                )
                
                claim_processor.submit_claim(claim)
                total_claims += 1
                
                # Store in database
                claim_data = {
                    'id': claim.id,
                    'patient_id': claim.patient_id,
                    'provider_id': claim.provider_id,
                    'amount': claim.amount,
                    'description': claim.description,
                    'date_of_service': claim.date_of_service.isoformat(),
                    'status': claim.status.value
                }
                db_manager.insert_claim(claim_data)
        
        # Verify all claims were processed
        assert total_claims == 50  # 10 patients * 5 claims each
        
        # Test retrieval performance
        all_approved = claim_processor.get_claims_by_status(ClaimStatus.APPROVED)
        assert len(all_approved) > 0  # Some small claims should be auto-approved
        
        # Test database statistics
        stats = db_manager.get_claim_statistics()
        assert stats['total_claims'] == 50
        assert 'approved' in stats['status_breakdown']
        
        # Test patient-specific queries
        for patient in patients[:3]:  # Test first 3 patients
            patient_claims = claim_processor.get_claims_by_patient(patient.id)
            assert len(patient_claims) == 5
            
            db_patient_claims = db_manager.get_claims_by_patient(patient.id)
            assert len(db_patient_claims) == 5