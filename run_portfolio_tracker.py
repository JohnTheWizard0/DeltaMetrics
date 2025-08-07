#!/usr/bin/env python3
"""
Portfolio Tracker Pro - Launcher Script with Diagnostics
Run this script from the project root directory.
"""

import sys
import os
import traceback
from pathlib import Path

def print_diagnostic_info():
    """Print diagnostic information"""
    print("🔍 Diagnostic Information:")
    print(f"   Python version: {sys.version}")
    print(f"   Current directory: {Path.cwd()}")
    print(f"   Script location: {Path(__file__).parent}")
    print(f"   Python path: {sys.path[:3]}...")  # Show first 3 entries
    print()

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_project_structure():
    """Check if we're in the right directory"""
    required_files = ['src/main.py', 'src/utils/config.py', 'requirements.txt']
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing project files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nEnsure you're running from the project root directory")
        return False
    
    print("✅ Project structure verified")
    return True

def main():
    """Main launcher function with detailed diagnostics"""
    print("🚀 Portfolio Tracker Pro - Launcher")
    print("=" * 50)
    
    # Print diagnostic info
    print_diagnostic_info()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check project structure
    if not check_project_structure():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Add project root to Python path
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"✅ Added to Python path: {project_root}")
    
    # Check required dependencies
    print("\n📦 Checking dependencies...")
    required_packages = [
        'flet', 'sqlalchemy', 'pydantic', 'pydantic_settings', 
        'cryptography', 'bcrypt', 'pandas', 'numpy', 'aiohttp'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError as e:
            print(f"   ❌ {package} - {e}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("\nInstall missing packages:")
        print("   pip install -r requirements.txt")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Try importing our modules
    print("\n🔧 Testing application imports...")
    try:
        print("   Testing src.utils.config...")
        from src.utils.config import get_config
        print("   ✅ Config module loaded")
        
        print("   Testing src.utils.crypto...")
        from src.utils.crypto import get_security_manager
        print("   ✅ Crypto module loaded")
        
        print("   Testing src.core.database...")
        from src.core.database import get_db_manager
        print("   ✅ Database module loaded")
        
        print("   Testing src.gui.dashboard...")
        from src.gui.dashboard import DashboardView
        print("   ✅ GUI module loaded")
        
        print("   Testing src.main...")
        from src.main import main as app_main
        print("   ✅ Main module loaded")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start the application
    print("\n🚀 Starting Portfolio Tracker Pro...")
    try:
        import flet as ft
        ft.app(target=app_main)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        print("\n📝 Full error details:")
        traceback.print_exc()
        print("\n🔧 Troubleshooting:")
        print("1. Try: pip install --upgrade -r requirements.txt")
        print("2. Check Windows Defender/antivirus isn't blocking")
        print("3. Try running as administrator")
        print("4. Restart your terminal/command prompt")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()