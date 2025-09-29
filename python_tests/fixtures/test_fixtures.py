"""
Test fixtures and utilities for Python tests

This module provides reusable fixtures, mock data, and utility functions
for testing the health insurance claim system.
"""

import pytest
import tempfile
import os
from datetime import date, datetime
from typing import Dict, List, Any
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python_src.claim_processor import (
    ClaimProcessor, Patient, Claim, ClaimStatus, UserType,
    AuthenticationService
)
from python_src.database import DatabaseManager


class MockData:
    """Class containing mock data for testing"""
    
    SAMPLE_PATIENTS = [
        {
            'id': 'P001',
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': date(1985, 3, 15),
            'insurance_id': 'INS123456789',
            'phone': '555-123-4567'
        },
        {
            'id': 'P002',
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'date_of_birth': date(1990, 7, 22),
            'insurance_id': 'INS987654321',
            'phone': '555-987-6543'
        },
        {
            'id': 'P003',
            'name': 'Robert Johnson',
            'email': 'robert.johnson@example.com',
            'date_of_birth': date(1978, 11, 8),
            'insurance_id': 'INS456789012',
            'phone': '555-456-7890'
        }
    ]
    
    SAMPLE_CLAIMS = [
        {
            'id': 'C001',
            'patient_id': 'P001',
            'provider_id': 'PR001',
            'amount': 75.0,
            'description': 'Annual wellness checkup',
            'date_of_service': date(2024, 1, 15),
            'status': ClaimStatus.PENDING
        },
        {
            'id': 'C002',
            'patient_id': 'P001',
            'provider_id': 'PR002',
            'amount': 250.0,
            'description': 'Blood work and lab tests',
            'date_of_service': date(2024, 1, 20),
            'status': ClaimStatus.PENDING
        },
        {
            'id': 'C003',
            'patient_id': 'P002',
            'provider_id': 'PR001',
            'amount': 500.0,
            'description': 'Specialist consultation',
            'date_of_service': date(2024, 1, 25),
            'status': ClaimStatus.PENDING
        },
        {
            'id': 'C004',
            'patient_id': 'P002',
            'provider_id': 'PR003',
            'amount': 15000.0,
            'description': 'Emergency surgery',
            'date_of_service': date(2024, 2, 1),
            'status': ClaimStatus.PENDING
        },
        {
            'id': 'C005',
            'patient_id': 'P003',
            'provider_id': 'PR002',
            'amount': 95.0,
            'description': 'Prescription medication',
            'date_of_service': date(2024, 2, 5),
            'status': ClaimStatus.PENDING
        }
    ]
    
    SAMPLE_USERS = [
        {
            'user_id': 'U001',
            'email': 'patient1@example.com',
            'password': 'patient123password',
            'user_type': UserType.PATIENT
        },
        {
            'user_id': 'U002',
            'email': 'provider1@hospital.com',
            'password': 'provider123password',
            'user_type': UserType.PROVIDER
        },
        {
            'user_id': 'U003',
            'email': 'payor1@insurance.com',
            'password': 'payor123password',
            'user_type': UserType.PAYOR
        }
    ]
    
    @classmethod
    def get_patient_objects(cls) -> List[Patient]:
        """Get list of Patient objects"""
        return [
            Patient(
                id=p['id'],
                name=p['name'],
                email=p['email'],
                date_of_birth=p['date_of_birth'],
                insurance_id=p['insurance_id'],
                phone=p.get('phone')
            )
            for p in cls.SAMPLE_PATIENTS
        ]
    
    @classmethod
    def get_claim_objects(cls) -> List[Claim]:
        """Get list of Claim objects"""
        return [
            Claim(
                id=c['id'],
                patient_id=c['patient_id'],
                provider_id=c['provider_id'],
                amount=c['amount'],
                description=c['description'],
                date_of_service=c['date_of_service'],
                status=c['status']
            )
            for c in cls.SAMPLE_CLAIMS
        ]
    
    @classmethod
    def get_database_patient_data(cls) -> List[Dict[str, Any]]:
        """Get patient data formatted for database insertion"""
        return [
            {
                'id': p['id'],
                'name': p['name'],
                'email': p['email'],
                'date_of_birth': p['date_of_birth'].isoformat(),
                'insurance_id': p['insurance_id'],
                'phone': p.get('phone')
            }
            for p in cls.SAMPLE_PATIENTS
        ]
    
    @classmethod
    def get_database_claim_data(cls) -> List[Dict[str, Any]]:
        """Get claim data formatted for database insertion"""
        return [
            {
                'id': c['id'],
                'patient_id': c['patient_id'],
                'provider_id': c['provider_id'],
                'amount': c['amount'],
                'description': c['description'],
                'date_of_service': c['date_of_service'].isoformat(),
                'status': c['status'].value
            }
            for c in cls.SAMPLE_CLAIMS
        ]


class TestDataBuilder:
    """Builder class for creating test data dynamically"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to initial state"""
        self._patients = []
        self._claims = []
        self._users = []
        return self
    
    def add_patient(self, patient_id: str = None, name: str = None, 
                   email: str = None, insurance_id: str = None) -> 'TestDataBuilder':
        """Add a patient to the builder"""
        patient_id = patient_id or f"P{len(self._patients) + 1:03d}"
        name = name or f"Test Patient {len(self._patients) + 1}"
        email = email or f"patient{len(self._patients) + 1}@test.com"
        insurance_id = insurance_id or f"INS{len(self._patients) + 1:09d}"
        
        patient = {
            'id': patient_id,
            'name': name,
            'email': email,
            'date_of_birth': date(1990, 1, 1),
            'insurance_id': insurance_id,
            'phone': f"555-{100 + len(self._patients):03d}-{1000 + len(self._patients):04d}"
        }
        
        self._patients.append(patient)
        return self
    
    def add_claim(self, claim_id: str = None, patient_id: str = None,
                 amount: float = None, description: str = None) -> 'TestDataBuilder':
        """Add a claim to the builder"""
        claim_id = claim_id or f"C{len(self._claims) + 1:03d}"
        patient_id = patient_id or (self._patients[0]['id'] if self._patients else 'P001')
        amount = amount or (100.0 + len(self._claims) * 50.0)
        description = description or f"Medical service {len(self._claims) + 1}"
        
        claim = {
            'id': claim_id,
            'patient_id': patient_id,
            'provider_id': f"PR{len(self._claims) % 3 + 1:03d}",
            'amount': amount,
            'description': description,
            'date_of_service': date(2024, 1, len(self._claims) + 1),
            'status': ClaimStatus.PENDING
        }
        
        self._claims.append(claim)
        return self
    
    def add_user(self, user_id: str = None, email: str = None,
                user_type: UserType = UserType.PATIENT) -> 'TestDataBuilder':
        """Add a user to the builder"""
        user_id = user_id or f"U{len(self._users) + 1:03d}"
        email = email or f"user{len(self._users) + 1}@test.com"
        
        user = {
            'user_id': user_id,
            'email': email,
            'password': f"password{len(self._users) + 1}23",
            'user_type': user_type
        }
        
        self._users.append(user)
        return self
    
    def with_multiple_patients(self, count: int) -> 'TestDataBuilder':
        """Add multiple patients"""
        for i in range(count):
            self.add_patient()
        return self
    
    def with_multiple_claims(self, count: int, patient_id: str = None) -> 'TestDataBuilder':
        """Add multiple claims"""
        for i in range(count):
            self.add_claim(patient_id=patient_id)
        return self
    
    def build_patients(self) -> List[Patient]:
        """Build Patient objects"""
        return [
            Patient(
                id=p['id'],
                name=p['name'],
                email=p['email'],
                date_of_birth=p['date_of_birth'],
                insurance_id=p['insurance_id'],
                phone=p['phone']
            )
            for p in self._patients
        ]
    
    def build_claims(self) -> List[Claim]:
        """Build Claim objects"""
        return [
            Claim(
                id=c['id'],
                patient_id=c['patient_id'],
                provider_id=c['provider_id'],
                amount=c['amount'],
                description=c['description'],
                date_of_service=c['date_of_service'],
                status=c['status']
            )
            for c in self._claims
        ]
    
    def build_users(self) -> List[Dict[str, Any]]:
        """Build user data"""
        return self._users.copy()


# Global fixtures
@pytest.fixture
def mock_data():
    """Fixture providing access to mock data"""
    return MockData()


@pytest.fixture
def test_data_builder():
    """Fixture providing a test data builder"""
    return TestDataBuilder()


@pytest.fixture
def fresh_claim_processor():
    """Fixture providing a fresh ClaimProcessor instance"""
    return ClaimProcessor()


@pytest.fixture
def fresh_auth_service():
    """Fixture providing a fresh AuthenticationService instance"""
    return AuthenticationService()


@pytest.fixture
def memory_db_manager():
    """Fixture providing an in-memory database manager"""
    return DatabaseManager(":memory:")


@pytest.fixture
def temp_db_manager():
    """Fixture providing a temporary file database manager"""
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
def populated_system():
    """Fixture providing a system populated with test data"""
    claim_processor = ClaimProcessor()
    auth_service = AuthenticationService()
    db_manager = DatabaseManager(":memory:")
    
    # Add test patients
    patients = MockData.get_patient_objects()
    for patient in patients:
        claim_processor.register_patient(patient)
        
        patient_data = {
            'id': patient.id,
            'name': patient.name,
            'email': patient.email,
            'date_of_birth': patient.date_of_birth.isoformat(),
            'insurance_id': patient.insurance_id,
            'phone': patient.phone
        }
        db_manager.insert_patient(patient_data)
    
    # Add test users
    for user_data in MockData.SAMPLE_USERS:
        auth_service.register_user(
            user_data['user_id'],
            user_data['email'],
            user_data['password'],
            user_data['user_type']
        )
    
    # Add test claims
    claims = MockData.get_claim_objects()
    for claim in claims:
        claim_processor.submit_claim(claim)
        
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
    
    return {
        'claim_processor': claim_processor,
        'auth_service': auth_service,
        'db_manager': db_manager,
        'patients': patients,
        'claims': claims
    }


# Utility functions for tests
def assert_patient_equal(patient1: Patient, patient2: Patient) -> None:
    """Assert that two patients are equal"""
    assert patient1.id == patient2.id
    assert patient1.name == patient2.name
    assert patient1.email == patient2.email
    assert patient1.date_of_birth == patient2.date_of_birth
    assert patient1.insurance_id == patient2.insurance_id
    assert patient1.phone == patient2.phone


def assert_claim_equal(claim1: Claim, claim2: Claim) -> None:
    """Assert that two claims are equal (excluding timestamps)"""
    assert claim1.id == claim2.id
    assert claim1.patient_id == claim2.patient_id
    assert claim1.provider_id == claim2.provider_id
    assert claim1.amount == claim2.amount
    assert claim1.description == claim2.description
    assert claim1.date_of_service == claim2.date_of_service
    assert claim1.status == claim2.status


def create_test_patient(patient_id: str = "TEST001", 
                       name: str = "Test Patient",
                       email: str = "test@example.com") -> Patient:
    """Create a test patient with specified or default values"""
    return Patient(
        id=patient_id,
        name=name,
        email=email,
        date_of_birth=date(1990, 1, 1),
        insurance_id=f"INS{patient_id}",
        phone="555-123-4567"
    )


def create_test_claim(claim_id: str = "TESTC001",
                     patient_id: str = "TEST001",
                     amount: float = 100.0,
                     description: str = "Test claim") -> Claim:
    """Create a test claim with specified or default values"""
    return Claim(
        id=claim_id,
        patient_id=patient_id,
        provider_id="TESTPR001",
        amount=amount,
        description=description,
        date_of_service=date(2024, 1, 1)
    )


def setup_test_database(db_manager: DatabaseManager) -> None:
    """Set up a test database with sample data"""
    # Add sample patients
    for patient_data in MockData.get_database_patient_data():
        db_manager.insert_patient(patient_data)
    
    # Add sample claims
    for claim_data in MockData.get_database_claim_data():
        db_manager.insert_claim(claim_data)


def cleanup_test_files(*file_paths: str) -> None:
    """Clean up test files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except OSError:
            pass  # Ignore cleanup errors in tests