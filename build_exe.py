"""
Build script for creating standalone executable with PyInstaller.
Optimized for minimal size and maximum performance.
"""

import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__


def clean_build_directories():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"Removed {spec_file}")


def build_executable():
    """Build the executable using PyInstaller."""
    
    # Base PyInstaller arguments
    args = [
        'src/main.py',  # Entry point
        '--name=PortfolioTracker',  # Executable name
        '--onefile',  # Single file executable
        '--windowed',  # No console window (GUI app)
        '--clean',  # Clean PyInstaller cache
        
        # Icon (if available)
        # '--icon=assets/icons/app.ico',
        
        # Optimize for size
        '--strip',  # Strip debug symbols
        '--noupx',  # Don't use UPX (can cause false antivirus positives)
        
        # Hidden imports for Flet and dependencies
        '--hidden-import=flet',
        '--hidden-import=flet.page',
        '--hidden-import=flet.app',
        '--hidden-import=sqlalchemy.sql.default_comparator',
        '--hidden-import=cryptography',
        '--hidden-import=bcrypt',
        '--hidden-import=argon2',
        
        # Add data files
        # '--add-data=assets;assets',
        
        # Paths
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        
        # Additional optimizations
        '--log-level=INFO',
    ]
    
    # Add Windows-specific options
    if sys.platform == 'win32':
        args.extend([
            '--version-file=version_info.txt',  # If version info exists
        ])
    
    print("Building executable with PyInstaller...")
    print(f"Arguments: {' '.join(args)}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print(f"Executable location: dist/PortfolioTracker{'.exe' if sys.platform == 'win32' else ''}")


def create_version_info():
    """Create version info file for Windows executable."""
    version_info = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    OS=0x40004,
    # The general type of file.
    fileType=0x1,
    # The function of the file.
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Portfolio Tracker Team'),
        StringStruct(u'FileDescription', u'Multi-Asset Portfolio Tracker'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'PortfolioTracker'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
        StringStruct(u'OriginalFilename', u'PortfolioTracker.exe'),
        StringStruct(u'ProductName', u'Portfolio Tracker Pro'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    if sys.platform == 'win32':
        with open('version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info)
        print("Created version_info.txt for Windows build")


def post_build_cleanup():
    """Perform post-build cleanup and optimization."""
    # Remove build directory
    if Path('build').exists():
        shutil.rmtree('build')
        print("Cleaned build directory")
    
    # Remove spec file
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"Removed {spec_file}")
    
    # Check executable size
    exe_name = 'PortfolioTracker.exe' if sys.platform == 'win32' else 'PortfolioTracker'
    exe_path = Path('dist') / exe_name
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\nExecutable size: {size_mb:.2f} MB")
        
        if size_mb > 120:
            print("⚠️  Warning: Executable size exceeds 120 MB target")
        else:
            print("✅ Executable size is within target range")


def main():
    """Main build process."""
    print("=" * 50)
    print("Portfolio Tracker - Build Process")
    print("=" * 50)
    
    # Clean previous builds
    print("\n1. Cleaning previous builds...")
    clean_build_directories()
    
    # Create version info for Windows
    if sys.platform == 'win32':
        print("\n2. Creating version info...")
        create_version_info()
    
    # Build executable
    print("\n3. Building executable...")
    build_executable()
    
    # Post-build cleanup
    print("\n4. Post-build cleanup...")
    post_build_cleanup()
    
    print("\n" + "=" * 50)
    print("Build process complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()