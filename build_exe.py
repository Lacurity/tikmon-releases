#!/usr/bin/env python3
"""
Build standalone executable for Karma Monitor
Your friend won't need Python installed!
"""

import os
import subprocess
import sys

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the standalone executable"""
    print("🔨 Building Karma Monitor executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # Hide console window (optional)
        "--name", "KarmaMonitor",       # Executable name
        "--icon", "icon.ico",           # Icon file (if you have one)
        "--add-data", "requirements.txt;.",  # Include requirements
        "tiktok_webhook_monitor.py"     # Main script
    ]
    
    # Remove icon option if no icon file exists
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon")
        cmd.remove("icon.ico")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Build complete! Check the 'dist' folder")
        print("📁 Your friend just needs the .exe file from dist/")
    except subprocess.CalledProcessError:
        print("❌ Build failed. Make sure PyInstaller is installed")
        return False
    
    return True

def main():
    """Main build process"""
    print("🎯 Karma Monitor - Executable Builder")
    print("=" * 50)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        print("\n🎉 SUCCESS!")
        print("📂 Send your friend: dist/KarmaMonitor.exe")
        print("🚀 They can run it directly - no Python needed!")
    else:
        print("\n❌ Build failed")

if __name__ == "__main__":
    main()