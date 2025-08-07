"""
Configuration management for the Portfolio Tracker application.
Handles app settings, constants, and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class AppConfig(BaseSettings):
    """Application configuration with validation."""
    
    # Application metadata
    APP_NAME: str = "Portfolio Tracker Pro"
    APP_VERSION: str = "1.0.0"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = Field(default_factory=lambda: Path.home() / ".portfolio_tracker")
    DB_PATH: Optional[Path] = None
    CACHE_DIR: Optional[Path] = None
    BACKUP_DIR: Optional[Path] = None
    LOG_DIR: Optional[Path] = None
    
    # Database settings
    DB_NAME: str = "portfolio.db"
    DB_BACKUP_COUNT: int = 5
    DB_WAL_MODE: bool = True
    
    # Security settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_SALT_ROUNDS: int = 12
    SESSION_TIMEOUT_MINUTES: int = 30
    ENCRYPTION_KEY_ITERATIONS: int = 100000
    
    # UI Settings
    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 900
    THEME_MODE: str = "dark"  # "dark", "light", "system"
    
    # Performance settings
    API_TIMEOUT_SECONDS: int = 30
    CACHE_TTL_SECONDS: int = 300
    MAX_CONCURRENT_API_CALLS: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_MAX_BYTES: int = 10_485_760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator("DB_PATH", "CACHE_DIR", "BACKUP_DIR", "LOG_DIR", pre=True, always=True)
    def set_paths(cls, v, values):
        """Initialize paths based on DATA_DIR."""
        if v is None and "DATA_DIR" in values:
            data_dir = values["DATA_DIR"]
            if not isinstance(data_dir, Path):
                data_dir = Path(data_dir)
            
            field_name = cls.__fields__[v].name if hasattr(cls, '__fields__') else ""
            
            if "DB_PATH" in str(v) or v is None and field_name == "DB_PATH":
                return data_dir / "database" / values.get("DB_NAME", "portfolio.db")
            elif "CACHE_DIR" in str(v) or v is None and field_name == "CACHE_DIR":
                return data_dir / "cache"
            elif "BACKUP_DIR" in str(v) or v is None and field_name == "BACKUP_DIR":
                return data_dir / "backups"
            elif "LOG_DIR" in str(v) or v is None and field_name == "LOG_DIR":
                return data_dir / "logs"
        return v
    
    def ensure_directories(self):
        """Create all necessary directories if they don't exist."""
        directories = [
            self.DATA_DIR,
            self.DB_PATH.parent if self.DB_PATH else None,
            self.CACHE_DIR,
            self.BACKUP_DIR,
            self.LOG_DIR
        ]
        
        for directory in directories:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)
    
    def get_db_url(self, encrypted: bool = True) -> str:
        """Get the database URL for SQLAlchemy."""
        if encrypted:
            # Will be used with sqlcipher or custom encryption
            return f"sqlite:///{self.DB_PATH}"
        return f"sqlite:///{self.DB_PATH}"


# Singleton instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the configuration singleton."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
        _config_instance.ensure_directories()
    return _config_instance


# Convenience constants
config = get_config()

# UI Color scheme (Material Design 3)
COLORS = {
    "primary": "#6750A4",
    "on_primary": "#FFFFFF",
    "secondary": "#625B71",
    "on_secondary": "#FFFFFF",
    "error": "#BA1A1A",
    "on_error": "#FFFFFF",
    "background": "#1C1B1F",
    "on_background": "#E6E1E5",
    "surface": "#1C1B1F",
    "on_surface": "#E6E1E5",
    "surface_variant": "#49454F",
    "on_surface_variant": "#CAC4D0",
    "outline": "#938F99",
    "success": "#4CAF50",
    "warning": "#FF9800",
}