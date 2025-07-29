#!/usr/bin/env python3
"""
NOVA Installation Check Script
Verifies that NOVA is properly installed and configured
"""

import sys
import importlib
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_required_modules():
    """Check if critical modules are available"""
    required_modules = [
        'yaml',
        'fastapi', 
        'uvicorn',
        'pydantic',
        'sqlalchemy',
        'aiohttp',  # Added for AI client
        'numpy',    # Added for compatibility
        'chromadb'  # Added for memory system
    ]
    
    missing = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - Available")
        except ImportError:
            print(f"❌ {module} - Missing")
            missing.append(module)
    
    return len(missing) == 0, missing

def check_nova_import():
    """Check if NOVA core modules can be imported"""
    try:
        from core.brain import NOVABrain
        print("✅ NOVA Brain - Available")
        return True
    except ImportError as e:
        print(f"❌ NOVA Brain - Import Error: {e}")
        return False

def check_config_files():
    """Check if configuration files exist"""
    import os
    config_files = [
        'config/config.yaml',
        'requirements.txt'
    ]
    
    all_present = True
    for file in config_files:
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            all_present = False
    
    return all_present

def main():
    """Main check routine"""
    print("🔍 NOVA Installation Check")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Modules", lambda: check_required_modules()[0]),
        ("NOVA Core", check_nova_import),
        ("Config Files", check_config_files)
    ]
    
    passed = 0
    failed = 0
    
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        try:
            if check_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 NOVA is ready to use!")
        print("\nNext steps:")
        print("1. Run: python main.py --help")
        print("2. Test: python main.py --god-mode 'Hello NOVA!'")
    else:
        print("🔧 Issues found. Try:")
        print("1. Run installation script: ./scripts/install.bat (Windows) or ./scripts/install.sh (Mac/Linux)")
        print("2. Install missing modules: pip install [module_name]")
        print("3. Check if you're in the NOVA directory")

if __name__ == "__main__":
    main()
