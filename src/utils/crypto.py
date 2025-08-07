"""
Security and encryption module for the Portfolio Tracker.
Handles master password, database encryption, and secure storage.
"""

import os
import base64
import hashlib
import json
from typing import Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.utils.config import get_config


class SecurityManager:
    """Manages all security operations including encryption and authentication."""
    
    def __init__(self):
        self.config = get_config()
        self._master_key: Optional[bytes] = None
        self._cipher: Optional[Fernet] = None
        self._session_expiry: Optional[datetime] = None
        self._auth_file = self.config.DATA_DIR / ".auth"
        
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive an encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.config.ENCRYPTION_KEY_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def hash_password(self, password: str) -> bytes:
        """Hash password using bcrypt for verification."""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=self.config.PASSWORD_SALT_ROUNDS)
        )
    
    def verify_password(self, password: str, hashed: bytes) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def initialize_master_password(self, password: str) -> bool:
        """
        Initialize the master password on first run.
        Creates auth file with hashed password and salt.
        """
        try:
            # Validate password strength
            if not self._validate_password_strength(password):
                return False
            
            # Generate salt for key derivation
            salt = os.urandom(16)
            
            # Hash password for verification
            password_hash = self.hash_password(password)
            
            # Store auth data
            auth_data = {
                "password_hash": base64.b64encode(password_hash).decode(),
                "salt": base64.b64encode(salt).decode(),
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Save auth file (this itself should be protected)
            self._auth_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._auth_file, 'w') as f:
                json.dump(auth_data, f)
            
            # Set file permissions (Windows/Unix compatible)
            try:
                os.chmod(self._auth_file, 0o600)
            except:
                pass  # Windows might not support chmod
            
            # Initialize encryption
            self._master_key = self.derive_key(password, salt)
            self._cipher = Fernet(self._master_key)
            self._session_expiry = datetime.now() + timedelta(
                minutes=self.config.SESSION_TIMEOUT_MINUTES
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize master password: {e}")
            return False
    
    def authenticate(self, password: str) -> bool:
        """
        Authenticate user with master password.
        Returns True if successful, False otherwise.
        """
        try:
            if not self._auth_file.exists():
                return False
            
            # Load auth data
            with open(self._auth_file, 'r') as f:
                auth_data = json.load(f)
            
            # Verify password
            password_hash = base64.b64decode(auth_data["password_hash"])
            if not self.verify_password(password, password_hash):
                return False
            
            # Initialize encryption
            salt = base64.b64decode(auth_data["salt"])
            self._master_key = self.derive_key(password, salt)
            self._cipher = Fernet(self._master_key)
            self._session_expiry = datetime.now() + timedelta(
                minutes=self.config.SESSION_TIMEOUT_MINUTES
            )
            
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated and session is valid."""
        if self._cipher is None or self._session_expiry is None:
            return False
        
        if datetime.now() > self._session_expiry:
            self.logout()
            return False
        
        return True
    
    def extend_session(self):
        """Extend the current session timeout."""
        if self.is_authenticated():
            self._session_expiry = datetime.now() + timedelta(
                minutes=self.config.SESSION_TIMEOUT_MINUTES
            )
    
    def logout(self):
        """Clear authentication state."""
        self._master_key = None
        self._cipher = None
        self._session_expiry = None
    
    def encrypt_data(self, data: Any) -> bytes:
        """Encrypt data using the master key."""
        if not self.is_authenticated():
            raise SecurityError("Not authenticated")
        
        if isinstance(data, str):
            data_bytes = data.encode()
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = json.dumps(data).encode()
        
        return self._cipher.encrypt(data_bytes)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using the master key."""
        if not self.is_authenticated():
            raise SecurityError("Not authenticated")
        
        return self._cipher.decrypt(encrypted_data)
    
    def encrypt_file(self, file_path: Path) -> Path:
        """Encrypt a file and return path to encrypted file."""
        if not self.is_authenticated():
            raise SecurityError("Not authenticated")
        
        with open(file_path, 'rb') as f:
            encrypted_data = self.encrypt_data(f.read())
        
        encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        return encrypted_path
    
    def decrypt_file(self, encrypted_path: Path) -> bytes:
        """Decrypt a file and return its contents."""
        if not self.is_authenticated():
            raise SecurityError("Not authenticated")
        
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        return self.decrypt_data(encrypted_data)
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets minimum requirements."""
        if len(password) < self.config.PASSWORD_MIN_LENGTH:
            return False
        
        # Check for at least one digit, one letter, and one special character
        has_digit = any(c.isdigit() for c in password)
        has_letter = any(c.isalpha() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return has_digit and has_letter and has_special
    
    def is_first_run(self) -> bool:
        """Check if this is the first run (no auth file exists)."""
        return not self._auth_file.exists()
    
    def get_password_requirements(self) -> str:
        """Get password requirements as a string."""
        return (
            f"Password must be at least {self.config.PASSWORD_MIN_LENGTH} characters long "
            "and contain at least one letter, one number, and one special character."
        )


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


# Singleton instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get or create the security manager singleton."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager