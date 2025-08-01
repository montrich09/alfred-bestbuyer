#!/usr/bin/env python3
"""
Launcher script for Best Buy Product Searcher
Checks dependencies and runs the main application
"""

import sys
import subprocess
import importlib.util

def check_dependency(module_name, package_name=None):
    """Check if a Python module is available"""
    if package_name is None:
        package_name = module_name
    
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ Missing dependency: {package_name}")
        return False
    else:
        print(f"✅ Found: {package_name}")
        return True

def install_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    print("🔍 Best Buy Product Searcher - Dependency Check")
    print("=" * 50)
    
    # Check required dependencies
    required_deps = [
        ("tkinter", "tkinter"),
        ("requests", "requests"),
        ("PIL", "Pillow"),
        ("bs4", "beautifulsoup4"),
        ("lxml", "lxml")
    ]
    
    missing_deps = []
    for module, package in required_deps:
        if not check_dependency(module, package):
            missing_deps.append(package)
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        response = input("Would you like to install them now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if install_dependencies():
                print("\n🚀 Starting application...")
                import bestbuy_searcher
                bestbuy_searcher.main()
            else:
                print("❌ Please install dependencies manually:")
                print("pip install -r requirements.txt")
        else:
            print("❌ Please install dependencies before running the application")
    else:
        print("\n✅ All dependencies found!")
        print("🚀 Starting application...")
        import bestbuy_searcher
        bestbuy_searcher.main()

if __name__ == "__main__":
    main() 