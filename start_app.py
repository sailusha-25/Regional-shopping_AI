#!/usr/bin/env python3
"""
Startup script for Regional Shopping AI application
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ('flask', 'flask'),
        ('flask_cors', 'flask-cors'),
        ('flask_sqlalchemy', 'flask-sqlalchemy'),
        ('sentence_transformers', 'sentence-transformers'),
        ('faiss', 'faiss-cpu'),
        ('numpy', 'numpy'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Copy .env.example to .env and configure your settings")
        return False
    
    print("✅ Environment file found")
    return True

def run_tests():
    """Run agent tests"""
    print("🧪 Running agent tests...")
    
    try:
        result = subprocess.run([sys.executable, 'test_agents.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ All agents are working properly")
            return True
        else:
            print("⚠️  Some agents have issues, but application can still run")
            print("Check test_agents.py output for details")
            return True  # Allow app to start even with some issues
            
    except subprocess.TimeoutExpired:
        print("⚠️  Agent tests timed out, but application can still run")
        return True
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return True  # Allow app to start anyway

def start_flask_app():
    """Start the Flask application"""
    print("🚀 Starting Regional Shopping AI application...")
    
    try:
        # Set environment variables
        os.environ['FLASK_APP'] = 'src/main.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Start the Flask app
        from src.main import app
        print("✅ Flask application loaded successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("📊 API endpoints available at http://localhost:5000/api/status")
        print("🛒 Shopping agents status at http://localhost:5000/api/shopping/agents/status")
        print("\n🔥 Press Ctrl+C to stop the server")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🎯 Regional Shopping AI - Startup Script")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check environment
    if not check_environment():
        return 1
    
    # Run tests
    run_tests()
    
    # Start application
    if not start_flask_app():
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)