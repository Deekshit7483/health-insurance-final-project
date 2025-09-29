"""
Database utilities for Health Insurance Claim Portal

This module provides database connection and utility functions.
"""

import sqlite3
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import json
from datetime import datetime, date


class DatabaseManager:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_path: str = "health_insurance.db"):
        """Initialize the database manager with the given database path."""
        self.db_path = db_path
        self.connection = None
        self._is_memory_db = db_path == ":memory:"
        
        # For in-memory databases, maintain a persistent connection
        if self._is_memory_db:
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
        
        self._create_tables()
    
    def initialize_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    date_of_birth DATE NOT NULL,
                    insurance_id TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create claims table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    provider_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    date_of_service DATE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_type TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self._is_memory_db and self.connection:
            # For in-memory databases, reuse the persistent connection
            yield self.connection
        else:
            # For file databases, create a new connection each time
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            try:
                yield conn
            finally:
                conn.close()
    
    def insert_patient(self, patient_data: Dict[str, Any]) -> bool:
        """Insert a new patient record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO patients (id, name, email, date_of_birth, insurance_id, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    patient_data['id'],
                    patient_data['name'],
                    patient_data['email'],
                    patient_data['date_of_birth'],
                    patient_data['insurance_id'],
                    patient_data.get('phone')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve patient by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def insert_claim(self, claim_data: Dict[str, Any]) -> bool:
        """Insert a new claim record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO claims (id, patient_id, provider_id, amount, description, 
                                      date_of_service, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    claim_data['id'],
                    claim_data['patient_id'],
                    claim_data['provider_id'],
                    claim_data['amount'],
                    claim_data['description'],
                    claim_data['date_of_service'],
                    claim_data['status']
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def update_claim_status(self, claim_id: str, status: str) -> bool:
        """Update claim status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE claims 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, claim_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_claims_by_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all claims for a patient"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM claims WHERE patient_id = ?', (patient_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_claims_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all claims with specific status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM claims WHERE status = ?', (status,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_claim_statistics(self) -> Dict[str, Any]:
        """Get claim statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total claims
            cursor.execute('SELECT COUNT(*) as total FROM claims')
            total_claims = cursor.fetchone()['total']
            
            # Claims by status
            cursor.execute('''
                SELECT status, COUNT(*) as count, AVG(amount) as avg_amount, SUM(amount) as total_amount
                FROM claims 
                GROUP BY status
            ''')
            status_stats = {row['status']: dict(row) for row in cursor.fetchall()}
            
            # Recent claims (last 30 days)
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM claims 
                WHERE created_at >= date('now', '-30 days')
            ''')
            recent_claims = cursor.fetchone()['count']
            
            return {
                'total_claims': total_claims,
                'status_breakdown': status_stats,
                'recent_claims_30_days': recent_claims
            }

    def _create_tables(self):
        """Create the necessary database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    date_of_birth TEXT,
                    insurance_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create claims table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    provider_id TEXT,
                    amount REAL NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    date_of_service TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Create users table (for authentication)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_type TEXT DEFAULT 'patient',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()


class DataValidator:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        # More strict email validation - no consecutive dots, no dots at start/end
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._+%-]*[a-zA-Z0-9])*@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])*\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False
        # Additional check for consecutive dots
        if '..' in email:
            return False
        return True
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Simple US phone number validation
        pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """Validate that end_date is after start_date"""
        return start_date <= end_date
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 100000.0) -> bool:
        """Validate monetary amount"""
        return min_amount <= amount <= max_amount


def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def export_claims_to_json(claims: List[Dict[str, Any]], filename: str) -> bool:
    """Export claims data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(claims, f, default=serialize_datetime, indent=2)
        return True
    except Exception:
        return False


def import_claims_from_json(filename: str) -> Optional[List[Dict[str, Any]]]:
    """Import claims data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception:
        return None