#!/usr/bin/env python3
"""
NOVA Quick Start Script

This script tests NOVA and then launches it if everything is working.
"""

import asyncio
import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import rich
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def run_tests():
    """Run NOVA tests"""
    print("\n🧪 Running NOVA tests...")
    print("=" * 50)
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test_nova.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def launch_nova():
    """Launch NOVA"""
    print("\n🚀 Launching NOVA...")
    print("=" * 50)
    
    try:
        # Check if we want CLI or web interface
        mode = input("\nChoose interface:\n1. CLI (default)\n2. Web + CLI\n3. Web only\nChoice (1-3): ").strip()
        
        if mode == "2":
            print("🌐 Starting NOVA with web interface...")
            subprocess.run([sys.executable, "main.py"])
        elif mode == "3":
            print("🌐 Starting NOVA web interface only...")
            subprocess.run([sys.executable, "main.py"])
        else:
            print("💻 Starting NOVA CLI...")
            subprocess.run([sys.executable, "main.py"])
            
    except KeyboardInterrupt:
        print("\n👋 NOVA startup cancelled")
    except Exception as e:
        print(f"❌ Failed to launch NOVA: {e}")

def show_welcome():
    """Show welcome message"""
    welcome = """
    🧠 Welcome to NOVA
    Neural Omnipresent Virtual Assistant
    
    ═══════════════════════════════════════════════════════════════
    
    🎯 What NOVA can do:
    • 🔍 Research and web search
    • 💻 Code generation and debugging  
    • 🔒 Cybersecurity monitoring
    • 📅 Life management and automation
    • 💰 Finance tracking and analysis
    • 📊 Data analysis and visualization
    • 🎨 Creative content generation
    • 🎓 Interactive learning assistance
    • 🚀 God Mode: Execute complex multi-step tasks
    
    ═══════════════════════════════════════════════════════════════
    """
    print(welcome)

def main():
    """Main launcher function"""
    show_welcome()
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 To install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("cache").mkdir(exist_ok=True)
    
    # Ask if user wants to run tests
    run_test = input("\n🧪 Run tests before launching? (y/N): ").strip().lower()
    
    if run_test in ['y', 'yes']:
        if not run_tests():
            print("\n❌ Tests failed. Please check the errors above.")
            choice = input("Continue anyway? (y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                sys.exit(1)
    
    # Launch NOVA
    launch_nova()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
