"""
Health Insurance Claim Processing Module

This module handles health insurance claim operations including validation,
processing, and status management.
"""

from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import re


class ClaimStatus(Enum):
    """Enumeration for claim statuses"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    REQUIRES_REVIEW = "requires_review"


class UserType(Enum):
    """Enumeration for user types"""
    PATIENT = "patient"
    PROVIDER = "provider"
    PAYOR = "payor"


@dataclass
class Patient:
    """Patient data model"""
    id: str
    name: str
    email: str
    date_of_birth: date
    insurance_id: str
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
            raise ValueError("Invalid email format")
        
        if not self.insurance_id:
            raise ValueError("Insurance ID is required")


@dataclass
class Claim:
    """Health insurance claim data model"""
    id: str
    patient_id: str
    provider_id: str
    amount: float
    description: str
    date_of_service: date
    status: ClaimStatus = ClaimStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        if self.amount <= 0:
            raise ValueError("Claim amount must be positive")
        
        if not self.description or len(self.description.strip()) < 5:
            raise ValueError("Claim description must be at least 5 characters")


class ClaimProcessor:
    """Main class for processing health insurance claims"""
    
    def __init__(self):
        self.claims: Dict[str, Claim] = {}
        self.patients: Dict[str, Patient] = {}
        self.auto_approve_threshold = 100.0
        self.max_claim_amount = 50000.0
    
    def register_patient(self, patient: Patient) -> bool:
        """Register a new patient"""
        if patient.id in self.patients:
            return False
        
        self.patients[patient.id] = patient
        return True
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Retrieve patient by ID"""
        return self.patients.get(patient_id)
    
    def submit_claim(self, claim: Claim) -> bool:
        """Submit a new claim for processing"""
        if claim.id in self.claims:
            return False
        
        if claim.patient_id not in self.patients:
            raise ValueError("Patient not found")
        
        if claim.amount > self.max_claim_amount:
            raise ValueError(f"Claim amount exceeds maximum limit of ${self.max_claim_amount}")
        
        self.claims[claim.id] = claim
        self._process_claim(claim)
        return True
    
    def _process_claim(self, claim: Claim) -> None:
        """Internal method to process claim based on business rules"""
        if claim.amount <= self.auto_approve_threshold:
            claim.status = ClaimStatus.APPROVED
        elif claim.amount > 10000.0:
            claim.status = ClaimStatus.REQUIRES_REVIEW
        else:
            claim.status = ClaimStatus.PROCESSING
        
        claim.updated_at = datetime.now()
    
    def approve_claim(self, claim_id: str) -> bool:
        """Manually approve a claim"""
        claim = self.claims.get(claim_id)
        if not claim:
            return False
        
        if claim.status in [ClaimStatus.APPROVED, ClaimStatus.REJECTED]:
            return False
        
        claim.status = ClaimStatus.APPROVED
        claim.updated_at = datetime.now()
        return True
    
    def reject_claim(self, claim_id: str, reason: str = "") -> bool:
        """Reject a claim with optional reason"""
        claim = self.claims.get(claim_id)
        if not claim:
            return False
        
        if claim.status in [ClaimStatus.APPROVED, ClaimStatus.REJECTED]:
            return False
        
        claim.status = ClaimStatus.REJECTED
        claim.updated_at = datetime.now()
        return True
    
    def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Retrieve claim by ID"""
        return self.claims.get(claim_id)
    
    def get_claims_by_patient(self, patient_id: str) -> List[Claim]:
        """Get all claims for a specific patient"""
        return [claim for claim in self.claims.values() if claim.patient_id == patient_id]
    
    def get_claims_by_status(self, status: ClaimStatus) -> List[Claim]:
        """Get all claims with a specific status"""
        return [claim for claim in self.claims.values() if claim.status == status]
    
    def calculate_total_approved_amount(self, patient_id: str) -> float:
        """Calculate total approved claim amount for a patient"""
        approved_claims = [
            claim for claim in self.claims.values() 
            if claim.patient_id == patient_id and claim.status == ClaimStatus.APPROVED
        ]
        return sum(claim.amount for claim in approved_claims)


class AuthenticationService:
    """Service for handling user authentication"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.active_sessions: Dict[str, str] = {}  # token -> user_id
    
    def register_user(self, user_id: str, email: str, password: str, user_type: UserType) -> bool:
        """Register a new user"""
        if user_id in self.users:
            return False
        
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("Invalid email format")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        self.users[user_id] = {
            'email': email,
            'password': password,  # In real app, this would be hashed
            'user_type': user_type,
            'created_at': datetime.now(),
            'is_active': True
        }
        return True
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        for user_id, user_data in self.users.items():
            if user_data['email'] == email and user_data['password'] == password:
                if user_data['is_active']:
                    return {
                        'user_id': user_id,
                        'email': email,
                        'user_type': user_data['user_type']
                    }
        return None
    
    def create_session(self, user_id: str) -> str:
        """Create a session token for authenticated user"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.active_sessions[token] = user_id
        return token
    
    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token and return user_id"""
        return self.active_sessions.get(token)
    
    def logout(self, token: str) -> bool:
        """Logout user by removing session"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False


def validate_insurance_id(insurance_id: str) -> bool:
    """Utility function to validate insurance ID format"""
    if not insurance_id:
        return False
    
    # Simple validation: should be alphanumeric and 8-12 characters
    return re.match(r'^[A-Z0-9]{8,12}$', insurance_id.upper()) is not None


def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"


def calculate_claim_processing_fee(amount: float) -> float:
    """Calculate processing fee based on claim amount"""
    if amount <= 1000:
        return 25.0
    elif amount <= 5000:
        return 50.0
    else:
        return 100.0