#!/usr/bin/env python3
"""
Quick Setup Script for Brain Tumor Detection Application
Run this to create all necessary directories and verify setup
"""

import os
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created: {path}")
    else:
        print(f"✓  Exists: {path}")

def check_file(path):
    """Check if file exists"""
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        return True
    else:
        print(f"❌ Missing: {path}")
        return False

def main():
    print("=" * 60)
    print("🧠 Brain Tumor Detection - Setup Script")
    print("=" * 60)
    print()
    
    # Check Python version
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        return
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    print()
    
    # Create directories
    print("Creating required directories...")
    directories = [
        "backend",
        "frontend",
        "model",
        "uploads",
        "reports",
        "static",
        "static/css",
        "static/js",
        "static/assets"
    ]
    
    for directory in directories:
        create_directory(directory)
    print()
    
    # Check critical files
    print("Checking critical files...")
    critical_files = [
        "backend/main.py",
        "backend/models.py",
        "backend/database.py",
        "backend/auth.py",
        "backend/prediction.py",
        "backend/pdf_generator.py",
        "backend/requirements.txt",
        "model/best_model.h5",
        "frontend/index.html",
        "frontend/signup.html",
        "frontend/dashboard.html"
    ]
    
    missing_files = []
    for file in critical_files:
        if not check_file(file):
            missing_files.append(file)
    print()
    
    # Summary
    print("=" * 60)
    if missing_files:
        print("⚠️  SETUP INCOMPLETE")
        print("\nMissing files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all files are in place before running the application.")
    else:
        print("✅ SETUP COMPLETE!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Start backend: cd backend && python main.py")
        print("3. Open frontend/index.html in your browser")
    print("=" * 60)

if __name__ == "__main__":
    main()