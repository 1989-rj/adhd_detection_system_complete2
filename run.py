#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADHD Detection System - Quick Start Script
Run this script to start the application after installing dependencies.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def run_application():
    """Start the Flask application"""
    print("Starting ADHD Detection System...")
    print("🚀 Application will be available at: http://localhost:5000")
    print("📱 The system is optimized for children aged 8-12")
    print("⚠️  Remember: This is for educational/screening purposes only")
    print("-" * 60)

    try:
        import app
        app.app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing app module: {e}")
        print("Please make sure you're in the correct directory and dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def main():
    print("🧠 ADHD Detection System - Setup and Launch")
    print("=" * 50)

    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found! Please ensure you're in the project directory.")
        return

    # Install dependencies
    if install_dependencies():
        print("\n" + "=" * 50)
        input("Press Enter to start the application...")
        run_application()
    else:
        print("❌ Setup failed. Please install dependencies manually:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
