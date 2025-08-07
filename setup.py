#!/usr/bin/env python3
"""
Portfolio Tracker Pro - Setup Script
Automated setup for the Portfolio Tracker project.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current version: {version.major}.{version.minor}.{version.micro}")
        print("Please install Python 3.11 or higher from https://python.org")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Try running manually: pip install -r requirements.txt")
        return False

def setup_project_structure():
    """Ensure proper project structure"""
    print("\n📁 Setting up project structure...")
    
    # Create __init__.py files if missing
    init_files = [
        "src/__init__.py",
        "src/gui/__init__.py",
        "src/core/__init__.py", 
        "src/utils/__init__.py",
        "src/models/__init__.py",
        "src/api/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.parent.mkdir(parents=True, exist_ok=True)
            init_path.write_text("# Auto-generated __init__.py\n")
            print(f"   Created: {init_file}")
    
    print("✅ Project structure verified")

def test_imports():
    """Test if all imports work"""
    print("\n🧪 Testing imports...")
    
    test_imports = [
        ("flet", "Flet GUI framework"),
        ("sqlalchemy", "SQLAlchemy ORM"),
        ("pydantic", "Pydantic validation"),
        ("pydantic_settings", "Pydantic settings"),
        ("cryptography", "Cryptography library"),
        ("bcrypt", "BCrypt password hashing"),
        ("pandas", "Pandas data processing"),
        ("numpy", "NumPy numerical computing"),
    ]
    
    failed_imports = []
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"   ✅ {description}")
        except ImportError:
            print(f"   ❌ {description}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful")
    return True

def create_launcher_scripts():
    """Create platform-specific launcher scripts"""
    print("\n🚀 Creating launcher scripts...")
    
    # Windows batch file
    windows_launcher = Path("run_portfolio_tracker.bat")
    windows_content = f"""@echo off
echo Starting Portfolio Tracker Pro...
python run_portfolio_tracker.py
pause
"""
    windows_launcher.write_text(windows_content)
    print("   Created: run_portfolio_tracker.bat (Windows)")
    
    # Unix shell script
    unix_launcher = Path("run_portfolio_tracker.sh")
    unix_content = f"""#!/bin/bash
echo "Starting Portfolio Tracker Pro..."
python3 run_portfolio_tracker.py
"""
    unix_launcher.write_text(unix_content)
    
    # Make shell script executable on Unix systems
    if os.name != 'nt':  # Not Windows
        try:
            unix_launcher.chmod(0o755)
        except:
            pass
    
    print("   Created: run_portfolio_tracker.sh (Linux/macOS)")
    print("✅ Launcher scripts created")

def main():
    """Main setup process"""
    print("🏗️  Portfolio Tracker Pro - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Setup project structure
    setup_project_structure()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Create launcher scripts
    create_launcher_scripts()
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n🚀 To run the application:")
    print("   Windows: double-click run_portfolio_tracker.bat")
    print("   Linux/macOS: ./run_portfolio_tracker.sh")
    print("   Or directly: python run_portfolio_tracker.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please resolve the issues above.")
        sys.exit(1)