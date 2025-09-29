"""
Unit tests for database module

These tests cover the DatabaseManager, DataValidator, and utility functions.
"""

import pytest
import sqlite3
import tempfile
import os
import json
from datetime import date, datetime
from unittest.mock import patch, mock_open
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python_src.database import (
    DatabaseManager, DataValidator, serialize_datetime,
    export_claims_to_json, import_claims_from_json
)


class TestDatabaseManager:
    """Test cases for DatabaseManager class"""
    
    @pytest.fixture
    def db_manager(self):
        """Fixture to provide a fresh in-memory database manager"""
        return DatabaseManager(":memory:")
    
    @pytest.fixture
    def temp_db_manager(self):
        """Fixture to provide a temporary file database manager"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            db_path = temp_file.name
        
        manager = DatabaseManager(db_path)
        yield manager
        
        # Cleanup
        try:
            os.unlink(db_path)
        except OSError:
            pass
    
    @pytest.fixture
    def sample_patient_data(self):
        """Fixture to provide sample patient data"""
        return {
            'id': 'P001',
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': '1990-01-01',
            'insurance_id': 'INS123456789',
            'phone': '555-123-4567'
        }
    
    @pytest.fixture
    def sample_claim_data(self):
        """Fixture to provide sample claim data"""
        return {
            'id': 'C001',
            'patient_id': 'P001',
            'provider_id': 'PR001',
            'amount': 250.50,
            'description': 'Annual checkup',
            'date_of_service': '2024-01-15',
            'status': 'pending'
        }
    
    def test_database_initialization(self, db_manager):
        """Test that database is initialized with correct tables"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('patients', 'claims', 'users')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'patients' in tables
            assert 'claims' in tables
            assert 'users' in tables
    
    def test_insert_patient_success(self, db_manager, sample_patient_data):
        """Test successful patient insertion"""
        result = db_manager.insert_patient(sample_patient_data)
        
        assert result is True
        
        # Verify patient was inserted
        patient = db_manager.get_patient('P001')
        assert patient is not None
        assert patient['name'] == 'John Doe'
        assert patient['email'] == 'john.doe@example.com'
    
    def test_insert_patient_duplicate_id(self, db_manager, sample_patient_data):
        """Test inserting patient with duplicate ID"""
        db_manager.insert_patient(sample_patient_data)
        result = db_manager.insert_patient(sample_patient_data)
        
        assert result is False
    
    def test_insert_patient_duplicate_email(self, db_manager, sample_patient_data):
        """Test inserting patient with duplicate email"""
        db_manager.insert_patient(sample_patient_data)
        
        # Try to insert another patient with same email but different ID
        duplicate_email_data = sample_patient_data.copy()
        duplicate_email_data['id'] = 'P002'
        result = db_manager.insert_patient(duplicate_email_data)
        
        assert result is False
    
    def test_get_patient_not_found(self, db_manager):
        """Test getting non-existent patient"""
        patient = db_manager.get_patient('NONEXISTENT')
        
        assert patient is None
    
    def test_insert_claim_success(self, db_manager, sample_patient_data, sample_claim_data):
        """Test successful claim insertion"""
        # First insert the patient
        db_manager.insert_patient(sample_patient_data)
        
        result = db_manager.insert_claim(sample_claim_data)
        
        assert result is True
    
    def test_insert_claim_duplicate_id(self, db_manager, sample_patient_data, sample_claim_data):
        """Test inserting claim with duplicate ID"""
        db_manager.insert_patient(sample_patient_data)
        db_manager.insert_claim(sample_claim_data)
        
        result = db_manager.insert_claim(sample_claim_data)
        
        assert result is False
    
    def test_update_claim_status_success(self, db_manager, sample_patient_data, sample_claim_data):
        """Test successful claim status update"""
        db_manager.insert_patient(sample_patient_data)
        db_manager.insert_claim(sample_claim_data)
        
        result = db_manager.update_claim_status('C001', 'approved')
        
        assert result is True
    
    def test_update_claim_status_not_found(self, db_manager):
        """Test updating status of non-existent claim"""
        result = db_manager.update_claim_status('NONEXISTENT', 'approved')
        
        assert result is False
    
    def test_get_claims_by_patient(self, db_manager, sample_patient_data):
        """Test retrieving claims by patient"""
        db_manager.insert_patient(sample_patient_data)
        
        # Insert multiple claims for the same patient
        claim1 = {
            'id': 'C001',
            'patient_id': 'P001',
            'provider_id': 'PR001',
            'amount': 100.0,
            'description': 'Checkup 1',
            'date_of_service': '2024-01-01',
            'status': 'pending'
        }
        
        claim2 = {
            'id': 'C002',
            'patient_id': 'P001',
            'provider_id': 'PR002',
            'amount': 200.0,
            'description': 'Checkup 2',
            'date_of_service': '2024-01-02',
            'status': 'approved'
        }
        
        db_manager.insert_claim(claim1)
        db_manager.insert_claim(claim2)
        
        claims = db_manager.get_claims_by_patient('P001')
        
        assert len(claims) == 2
        claim_ids = [claim['id'] for claim in claims]
        assert 'C001' in claim_ids
        assert 'C002' in claim_ids
    
    def test_get_claims_by_status(self, db_manager, sample_patient_data):
        """Test retrieving claims by status"""
        db_manager.insert_patient(sample_patient_data)
        
        # Insert claims with different statuses
        pending_claim = {
            'id': 'C001',
            'patient_id': 'P001',
            'provider_id': 'PR001',
            'amount': 100.0,
            'description': 'Pending claim',
            'date_of_service': '2024-01-01',
            'status': 'pending'
        }
        
        approved_claim = {
            'id': 'C002',
            'patient_id': 'P001',
            'provider_id': 'PR002',
            'amount': 200.0,
            'description': 'Approved claim',
            'date_of_service': '2024-01-02',
            'status': 'approved'
        }
        
        db_manager.insert_claim(pending_claim)
        db_manager.insert_claim(approved_claim)
        
        pending_claims = db_manager.get_claims_by_status('pending')
        approved_claims = db_manager.get_claims_by_status('approved')
        
        assert len(pending_claims) == 1
        assert len(approved_claims) == 1
        assert pending_claims[0]['id'] == 'C001'
        assert approved_claims[0]['id'] == 'C002'
    
    def test_get_claim_statistics(self, db_manager, sample_patient_data):
        """Test getting claim statistics"""
        db_manager.insert_patient(sample_patient_data)
        
        # Insert claims with different statuses and amounts
        claims = [
            {'id': 'C001', 'patient_id': 'P001', 'provider_id': 'PR001', 
             'amount': 100.0, 'description': 'Claim 1', 'date_of_service': '2024-01-01', 'status': 'pending'},
            {'id': 'C002', 'patient_id': 'P001', 'provider_id': 'PR002', 
             'amount': 200.0, 'description': 'Claim 2', 'date_of_service': '2024-01-02', 'status': 'approved'},
            {'id': 'C003', 'patient_id': 'P001', 'provider_id': 'PR003', 
             'amount': 300.0, 'description': 'Claim 3', 'date_of_service': '2024-01-03', 'status': 'approved'},
        ]
        
        for claim in claims:
            db_manager.insert_claim(claim)
        
        stats = db_manager.get_claim_statistics()
        
        assert stats['total_claims'] == 3
        assert 'pending' in stats['status_breakdown']
        assert 'approved' in stats['status_breakdown']
        assert stats['status_breakdown']['pending']['count'] == 1
        assert stats['status_breakdown']['approved']['count'] == 2
        assert stats['recent_claims_30_days'] == 3  # All claims are recent
    
    def test_connection_context_manager(self, temp_db_manager):
        """Test that connection context manager works correctly"""
        with temp_db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        
        # Connection should be closed after exiting context


class TestDataValidator:
    """Test cases for DataValidator class"""
    
    def test_validate_email_valid(self):
        """Test valid email validation"""
        valid_emails = [
            'user@example.com',
            'test.email@domain.org',
            'user+tag@example.co.uk',
            'firstname.lastname@company.com'
        ]
        
        for email in valid_emails:
            assert DataValidator.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user..double.dot@example.com',
            'user@example',
            ''
        ]
        
        for email in invalid_emails:
            assert DataValidator.validate_email(email) is False
    
    def test_validate_phone_valid(self):
        """Test valid phone number validation"""
        valid_phones = [
            '555-123-4567',
            '(555) 123-4567',
            '555 123 4567',
            '5551234567',
            '+1-555-123-4567',
            '1-555-123-4567'
        ]
        
        for phone in valid_phones:
            assert DataValidator.validate_phone(phone) is True
    
    def test_validate_phone_invalid(self):
        """Test invalid phone number validation"""
        invalid_phones = [
            '123-456',  # Too short
            '123-456-78901',  # Too long
            'abc-def-ghij',  # Non-numeric
            '',  # Empty
            '555-123-456a'  # Contains letter
        ]
        
        for phone in invalid_phones:
            assert DataValidator.validate_phone(phone) is False
    
    def test_validate_date_range_valid(self):
        """Test valid date range validation"""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        assert DataValidator.validate_date_range(start_date, end_date) is True
        
        # Same date should be valid
        assert DataValidator.validate_date_range(start_date, start_date) is True
    
    def test_validate_date_range_invalid(self):
        """Test invalid date range validation"""
        start_date = date(2024, 1, 31)
        end_date = date(2024, 1, 1)
        
        assert DataValidator.validate_date_range(start_date, end_date) is False
    
    def test_validate_amount_valid(self):
        """Test valid amount validation"""
        assert DataValidator.validate_amount(100.0) is True
        assert DataValidator.validate_amount(0.01) is True  # Minimum
        assert DataValidator.validate_amount(100000.0) is True  # Maximum
        assert DataValidator.validate_amount(50000.0) is True  # Middle
    
    def test_validate_amount_invalid(self):
        """Test invalid amount validation"""
        assert DataValidator.validate_amount(0.0) is False  # Below minimum
        assert DataValidator.validate_amount(-100.0) is False  # Negative
        assert DataValidator.validate_amount(200000.0) is False  # Above maximum
    
    def test_validate_amount_custom_range(self):
        """Test amount validation with custom range"""
        assert DataValidator.validate_amount(50.0, min_amount=10.0, max_amount=100.0) is True
        assert DataValidator.validate_amount(5.0, min_amount=10.0, max_amount=100.0) is False
        assert DataValidator.validate_amount(150.0, min_amount=10.0, max_amount=100.0) is False


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_serialize_datetime(self):
        """Test datetime serialization for JSON"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        test_date = date(2024, 1, 15)
        
        assert serialize_datetime(test_datetime) == '2024-01-15T10:30:45'
        assert serialize_datetime(test_date) == '2024-01-15'
    
    def test_serialize_datetime_invalid_type(self):
        """Test datetime serialization with invalid type"""
        with pytest.raises(TypeError):
            serialize_datetime("not a datetime")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_export_claims_to_json_success(self, mock_json_dump, mock_file):
        """Test successful claims export to JSON"""
        claims_data = [
            {'id': 'C001', 'amount': 100.0, 'status': 'approved'},
            {'id': 'C002', 'amount': 200.0, 'status': 'pending'}
        ]
        
        result = export_claims_to_json(claims_data, 'test_claims.json')
        
        assert result is True
        mock_file.assert_called_once_with('test_claims.json', 'w')
        mock_json_dump.assert_called_once_with(
            claims_data, 
            mock_file.return_value.__enter__.return_value,
            default=serialize_datetime,
            indent=2
        )
    
    @patch('builtins.open', side_effect=IOError("File not found"))
    def test_export_claims_to_json_failure(self, mock_file):
        """Test claims export failure"""
        claims_data = [{'id': 'C001', 'amount': 100.0}]
        
        result = export_claims_to_json(claims_data, 'invalid_path/test_claims.json')
        
        assert result is False
    
    @patch('builtins.open', new_callable=mock_open, read_data='[{"id": "C001", "amount": 100.0}]')
    @patch('json.load')
    def test_import_claims_from_json_success(self, mock_json_load, mock_file):
        """Test successful claims import from JSON"""
        expected_data = [{'id': 'C001', 'amount': 100.0}]
        mock_json_load.return_value = expected_data
        
        result = import_claims_from_json('test_claims.json')
        
        assert result == expected_data
        mock_file.assert_called_once_with('test_claims.json', 'r')
        mock_json_load.assert_called_once()
    
    @patch('builtins.open', side_effect=IOError("File not found"))
    def test_import_claims_from_json_failure(self, mock_file):
        """Test claims import failure"""
        result = import_claims_from_json('nonexistent_file.json')
        
        assert result is None


class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_complete_patient_claim_workflow(self):
        """Test complete workflow with patient and claim operations"""
        db_manager = DatabaseManager(":memory:")
        
        # Step 1: Insert patient
        patient_data = {
            'id': 'P001',
            'name': 'Alice Johnson',
            'email': 'alice.johnson@example.com',
            'date_of_birth': '1988-03-20',
            'insurance_id': 'INS555666777',
            'phone': '555-987-6543'
        }
        
        assert db_manager.insert_patient(patient_data) is True
        
        # Step 2: Insert claims
        claims_data = [
            {
                'id': 'C001',
                'patient_id': 'P001',
                'provider_id': 'PR001',
                'amount': 150.0,
                'description': 'Regular checkup',
                'date_of_service': '2024-01-10',
                'status': 'pending'
            },
            {
                'id': 'C002',
                'patient_id': 'P001',
                'provider_id': 'PR002',
                'amount': 300.0,
                'description': 'Blood tests',
                'date_of_service': '2024-01-15',
                'status': 'pending'
            }
        ]
        
        for claim_data in claims_data:
            assert db_manager.insert_claim(claim_data) is True
        
        # Step 3: Update claim statuses
        assert db_manager.update_claim_status('C001', 'approved') is True
        assert db_manager.update_claim_status('C002', 'rejected') is True
        
        # Step 4: Verify data
        patient = db_manager.get_patient('P001')
        assert patient['name'] == 'Alice Johnson'
        
        patient_claims = db_manager.get_claims_by_patient('P001')
        assert len(patient_claims) == 2
        
        approved_claims = db_manager.get_claims_by_status('approved')
        rejected_claims = db_manager.get_claims_by_status('rejected')
        
        assert len(approved_claims) == 1
        assert len(rejected_claims) == 1
        assert approved_claims[0]['id'] == 'C001'
        assert rejected_claims[0]['id'] == 'C002'
        
        # Step 5: Check statistics
        stats = db_manager.get_claim_statistics()
        assert stats['total_claims'] == 2
        assert stats['status_breakdown']['approved']['count'] == 1
        assert stats['status_breakdown']['rejected']['count'] == 1