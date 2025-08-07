"""
Database management module with encryption support.
Handles SQLite database operations with ACID compliance.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Dict, List
from contextlib import contextmanager

from sqlalchemy import create_engine, text, event, Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.utils.config import get_config
from src.utils.crypto import get_security_manager, SecurityError


Base = declarative_base()


class Account(Base):
    """Account/Depot model for storing trading accounts."""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # 'stocks', 'crypto', 'mixed'
    broker = Column(String(100))  # Broker/Exchange name
    currency = Column(String(3), default='EUR')
    initial_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata_encrypted = Column(Text)  # Encrypted JSON for sensitive data


class Asset(Base):
    """Asset model for stocks, ETFs, and cryptocurrencies."""
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    name = Column(String(200))
    asset_type = Column(String(20), nullable=False)  # 'stock', 'etf', 'crypto'
    exchange = Column(String(50))
    currency = Column(String(3))
    last_price = Column(Float)
    last_updated = Column(DateTime)
    metadata_encrypted = Column(Text)


class Transaction(Base):
    """Transaction model for all buy/sell operations."""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    asset_id = Column(Integer)
    transaction_type = Column(String(20), nullable=False)  # 'buy', 'sell', 'dividend', 'fee'
    quantity = Column(Float)
    price = Column(Float)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    fee = Column(Float, default=0.0)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    metadata_encrypted = Column(Text)


class PortfolioSnapshot(Base):
    """Snapshot of portfolio value at specific points in time."""
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(DateTime, nullable=False)
    total_value_eur = Column(Float, nullable=False)
    total_value_usd = Column(Float)
    cash_eur = Column(Float, default=0.0)
    cash_usd = Column(Float, default=0.0)
    metadata_encrypted = Column(Text)


class Settings(Base):
    """Application settings storage."""
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)
    encrypted = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    """Manages database operations with encryption support."""
    
    def __init__(self):
        self.config = get_config()
        self.security = get_security_manager()
        self.engine = None
        self.Session = None
        self._initialized = False
    
    def initialize(self, check_auth: bool = True) -> bool:
        """
        Initialize the database connection.
        Creates tables if they don't exist.
        """
        try:
            if check_auth and not self.security.is_authenticated():
                raise SecurityError("Not authenticated")
            
            # Create database directory
            self.config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            # Create engine with WAL mode for better concurrency
            self.engine = create_engine(
                f"sqlite:///{self.config.DB_PATH}",
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                poolclass=StaticPool,
                echo=False
            )
            
            # Enable WAL mode and other optimizations
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                if self.config.DB_WAL_MODE:
                    cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA mmap_size=30000000000")
                cursor.close()
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            # Initialize default settings if first run
            if self._is_first_db_run():
                self._initialize_defaults()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions with automatic rollback on error."""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def encrypt_field(self, data: Any) -> str:
        """Encrypt data for storage in database."""
        if data is None:
            return None
        
        json_str = json.dumps(data) if not isinstance(data, str) else data
        encrypted = self.security.encrypt_data(json_str)
        return encrypted.hex()
    
    def decrypt_field(self, encrypted_hex: str) -> Any:
        """Decrypt data from database."""
        if not encrypted_hex:
            return None
        
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        decrypted = self.security.decrypt_data(encrypted_bytes)
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted.decode()
    
    def create_account(self, name: str, account_type: str, broker: str = None,
                      currency: str = 'EUR', initial_balance: float = 0.0) -> int:
        """Create a new account/depot."""
        with self.get_session() as session:
            account = Account(
                name=name,
                account_type=account_type,
                broker=broker,
                currency=currency,
                initial_balance=initial_balance
            )
            
            # Encrypt sensitive metadata if needed
            if broker:
                metadata = {"broker_details": broker}
                account.metadata_encrypted = self.encrypt_field(metadata)
            
            session.add(account)
            session.flush()
            return account.id
    
    def get_accounts(self, active_only: bool = True) -> List[Dict]:
        """Get all accounts."""
        with self.get_session() as session:
            query = session.query(Account)
            if active_only:
                query = query.filter(Account.is_active == True)
            
            accounts = []
            for acc in query.all():
                account_dict = {
                    'id': acc.id,
                    'name': acc.name,
                    'type': acc.account_type,
                    'broker': acc.broker,
                    'currency': acc.currency,
                    'initial_balance': acc.initial_balance,
                    'created_at': acc.created_at.isoformat() if acc.created_at else None,
                    'is_active': acc.is_active
                }
                
                # Decrypt metadata if present
                if acc.metadata_encrypted:
                    try:
                        account_dict['metadata'] = self.decrypt_field(acc.metadata_encrypted)
                    except:
                        pass
                
                accounts.append(account_dict)
            
            return accounts
    
    def save_setting(self, key: str, value: Any, encrypted: bool = False) -> bool:
        """Save a setting to the database."""
        try:
            with self.get_session() as session:
                # Check if setting exists
                setting = session.query(Settings).filter_by(key=key).first()
                
                # Prepare value
                if encrypted:
                    value_str = self.encrypt_field(value)
                else:
                    value_str = json.dumps(value) if not isinstance(value, str) else value
                
                if setting:
                    setting.value = value_str
                    setting.encrypted = encrypted
                    setting.updated_at = datetime.utcnow()
                else:
                    setting = Settings(
                        key=key,
                        value=value_str,
                        encrypted=encrypted
                    )
                    session.add(setting)
                
                return True
        except Exception as e:
            print(f"Failed to save setting: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from the database."""
        try:
            with self.get_session() as session:
                setting = session.query(Settings).filter_by(key=key).first()
                
                if not setting:
                    return default
                
                if setting.encrypted:
                    return self.decrypt_field(setting.value)
                else:
                    try:
                        return json.loads(setting.value)
                    except json.JSONDecodeError:
                        return setting.value
        except Exception as e:
            print(f"Failed to get setting: {e}")
            return default
    
    def verify_integrity(self) -> bool:
        """Verify database integrity."""
        try:
            with self.get_session() as session:
                # Run integrity check
                result = session.execute(text("PRAGMA integrity_check"))
                integrity = result.scalar()
                
                if integrity != "ok":
                    print(f"Database integrity check failed: {integrity}")
                    return False
                
                # Check table existence
                tables = ['accounts', 'assets', 'transactions', 'portfolio_snapshots', 'settings']
                for table in tables:
                    result = session.execute(
                        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
                        {"name": table}
                    )
                    if not result.scalar():
                        print(f"Table {table} missing")
                        return False
                
                return True
                
        except Exception as e:
            print(f"Integrity check failed: {e}")
            return False
    
    def backup_database(self) -> Optional[Path]:
        """Create a backup of the database."""
        try:
            if not self.config.DB_PATH.exists():
                return None
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config.BACKUP_DIR / f"portfolio_backup_{timestamp}.db"
            
            # Ensure backup directory exists
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup using SQLite backup API
            source = sqlite3.connect(str(self.config.DB_PATH))
            dest = sqlite3.connect(str(backup_path))
            
            with dest:
                source.backup(dest)
            
            source.close()
            dest.close()
            
            # Encrypt the backup if authenticated
            if self.security.is_authenticated():
                encrypted_backup = self.security.encrypt_file(backup_path)
                backup_path.unlink()  # Remove unencrypted backup
                return encrypted_backup
            
            return backup_path
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return None
    
    def _is_first_db_run(self) -> bool:
        """Check if this is the first database run."""
        with self.get_session() as session:
            count = session.query(Settings).count()
            return count == 0
    
    def _initialize_defaults(self):
        """Initialize default settings on first run."""
        defaults = {
            "app_version": self.config.APP_VERSION,
            "db_version": "1.0",
            "first_run_date": datetime.utcnow().isoformat(),
            "theme": self.config.THEME_MODE,
            "currency_primary": "EUR",
            "currency_secondary": "USD"
        }
        
        for key, value in defaults.items():
            self.save_setting(key, value)


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get or create the database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager