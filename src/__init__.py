# src/__init__.py
"""Portfolio Tracker - Multi-asset portfolio management application."""

__version__ = "1.0.0"
__author__ = "Portfolio Tracker Team"

# src/gui/__init__.py
"""GUI components for the Portfolio Tracker application."""

from .dashboard import DashboardView

__all__ = ['DashboardView']

# src/utils/__init__.py
"""Utility modules for configuration, security, and helpers."""

from .config import get_config, COLORS
from .crypto import get_security_manager, SecurityError

__all__ = ['get_config', 'COLORS', 'get_security_manager', 'SecurityError']

# src/core/__init__.py
"""Core business logic and database operations."""

from .database import get_db_manager, DatabaseManager

__all__ = ['get_db_manager', 'DatabaseManager']

# src/api/__init__.py
"""API integration modules for stocks, crypto, and currencies."""

# This will be populated as we add API integrations

# src/models/__init__.py
"""Data models for portfolio, assets, and transactions."""

# This will be populated with Pydantic models