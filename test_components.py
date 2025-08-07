#!/usr/bin/env python3
"""
Component Test Script - Portfolio Tracker Pro
Tests each component individually to identify issues.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test basic Python imports"""
    print("1️⃣ Testing basic imports...")
    try:
        import json
        import sqlite3
        import datetime
        print("   ✅ Standard library imports work")
        return True
    except Exception as e:
        print(f"   ❌ Standard library error: {e}")
        return False

def test_external_packages():
    """Test external package imports"""
    print("\n2️⃣ Testing external packages...")
    packages = {
        'flet': 'GUI Framework',
        'sqlalchemy': 'Database ORM',
        'pydantic': 'Data Validation',
        'cryptography': 'Encryption',
        'bcrypt': 'Password Hashing',
        'pandas': 'Data Processing',
        'numpy': 'Numerical Computing',
    }
    
    failed = []
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"   ✅ {description} ({package})")
        except ImportError as e:
            print(f"   ❌ {description} ({package}): {e}")
            failed.append(package)
    
    return len(failed) == 0

def test_config_module():
    """Test config module"""
    print("\n3️⃣ Testing config module...")
    try:
        from src.utils.config import get_config, COLORS
        config = get_config()
        print(f"   ✅ Config loaded: {config.APP_NAME} v{config.APP_VERSION}")
        print(f"   ✅ Colors loaded: {len(COLORS)} color definitions")
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crypto_module():
    """Test crypto module"""
    print("\n4️⃣ Testing crypto module...")
    try:
        from src.utils.crypto import get_security_manager
        security = get_security_manager()
        print(f"   ✅ Security manager created")
        print(f"   ✅ First run check: {security.is_first_run()}")
        return True
    except Exception as e:
        print(f"   ❌ Crypto error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_module():
    """Test database module"""
    print("\n5️⃣ Testing database module...")
    try:
        from src.core.database import get_db_manager
        db = get_db_manager()
        print(f"   ✅ Database manager created")
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_module():
    """Test GUI module"""
    print("\n6️⃣ Testing GUI module...")
    try:
        from src.gui.dashboard import DashboardView
        print(f"   ✅ Dashboard view module loaded")
        return True
    except Exception as e:
        print(f"   ❌ GUI error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_module():
    """Test main module"""
    print("\n7️⃣ Testing main module...")
    try:
        from src.main import PortfolioTrackerApp, AuthenticationView
        print(f"   ✅ Main application classes loaded")
        return True
    except Exception as e:
        print(f"   ❌ Main module error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flet_basic():
    """Test basic Flet functionality"""
    print("\n8️⃣ Testing Flet basic functionality...")
    try:
        import flet as ft
        
        # Test basic Flet components
        text = ft.Text("Test")
        button = ft.ElevatedButton("Test Button")
        container = ft.Container(content=text)
        icon = ft.Icon(ft.Icons.HOME)  # Test with correct capitalization
        
        print("   ✅ Flet components can be created")
        return True
    except Exception as e:
        print(f"   ❌ Flet basic test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Portfolio Tracker Pro - Component Tests")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_external_packages,
        test_config_module,
        test_crypto_module,
        test_database_module,
        test_gui_module,
        test_main_module,
        test_flet_basic,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The application should work.")
        print("\n🚀 Try running: python run_portfolio_tracker.py")
    else:
        print(f"❌ {total - passed} tests failed. Fix the issues above first.")
        print("\n💡 Common fixes:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Update packages: pip install --upgrade -r requirements.txt")
        print("   - Check Python version: python --version (needs 3.11+)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)