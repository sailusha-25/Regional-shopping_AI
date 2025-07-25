#!/usr/bin/env python3
"""
Smart dependency installer for Regional Shopping AI
Handles Python 3.13 compatibility issues and provides fallbacks
"""

import sys
import subprocess
import importlib
import os

def check_python_version():
    """Check Python version and warn about compatibility"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13+ detected - some packages may need special handling")
        return True
    return False

def install_package(package_name, fallback_versions=None):
    """Install a package with fallback versions"""
    print(f"📦 Installing {package_name}...")
    
    # Try main package first
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
    except subprocess.TimeoutExpired:
        print(f"⏰ {package_name} installation timed out")
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
    
    # Try fallback versions
    if fallback_versions:
        for fallback in fallback_versions:
            print(f"🔄 Trying fallback: {fallback}")
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', fallback], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print(f"✅ {fallback} installed successfully")
                    return True
            except Exception as e:
                print(f"❌ Fallback {fallback} failed: {e}")
    
    return False

def install_core_dependencies():
    """Install core dependencies that are essential"""
    core_packages = {
        'flask': ['Flask>=2.3.0', 'Flask==2.3.3'],
        'flask-cors': ['Flask-CORS>=3.0.0', 'Flask-CORS==3.0.10'],
        'flask-sqlalchemy': ['Flask-SQLAlchemy>=2.5.0', 'Flask-SQLAlchemy==2.5.1'],
        'requests': ['requests>=2.28.0'],
        'python-dotenv': ['python-dotenv>=0.19.0'],
        'beautifulsoup4': ['beautifulsoup4>=4.11.0'],
        'langdetect': ['langdetect>=1.0.7']
    }
    
    print("🔧 Installing core dependencies...")
    success_count = 0
    
    for package, versions in core_packages.items():
        if install_package(versions[0], versions[1:] if len(versions) > 1 else None):
            success_count += 1
    
    return success_count, len(core_packages)

def install_ai_dependencies():
    """Install AI/ML dependencies with special handling for Python 3.13"""
    print("🤖 Installing AI/ML dependencies...")
    
    # Check if we can install the full AI stack
    ai_packages = [
        ('numpy', ['numpy>=1.24.0', 'numpy==1.24.4']),
        ('scikit-learn', ['scikit-learn>=1.3.0', 'scikit-learn==1.3.2']),
    ]
    
    success_count = 0
    for package_name, versions in ai_packages:
        if install_package(versions[0], versions[1:]):
            success_count += 1
    
    # Try sentence-transformers with special handling
    print("📝 Installing sentence-transformers...")
    sentence_transformers_installed = False
    
    # Try different approaches for sentence-transformers
    approaches = [
        'sentence-transformers>=2.2.0',
        'sentence-transformers==2.2.2',
        '--no-deps sentence-transformers==2.2.2'
    ]
    
    for approach in approaches:
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + approach.split()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                sentence_transformers_installed = True
                print("✅ sentence-transformers installed successfully")
                break
        except Exception as e:
            print(f"❌ Approach '{approach}' failed: {e}")
    
    if sentence_transformers_installed:
        success_count += 1
    
    # Try faiss-cpu with special handling
    print("🔍 Installing faiss-cpu...")
    faiss_installed = False
    
    faiss_approaches = [
        'faiss-cpu>=1.7.0',
        'faiss-cpu==1.7.4',
        '--no-deps faiss-cpu==1.7.4'
    ]
    
    for approach in faiss_approaches:
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + approach.split()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                faiss_installed = True
                print("✅ faiss-cpu installed successfully")
                break
        except Exception as e:
            print(f"❌ Faiss approach '{approach}' failed: {e}")
    
    if faiss_installed:
        success_count += 1
    
    return success_count, len(ai_packages) + 2  # +2 for sentence-transformers and faiss

def create_minimal_fallback():
    """Create minimal fallback implementations for missing dependencies"""
    print("🔧 Creating fallback implementations...")
    
    fallback_dir = "src/fallbacks"
    os.makedirs(fallback_dir, exist_ok=True)
    
    # Create minimal sentence transformer fallback
    fallback_sentence_transformer = '''
"""
Minimal fallback for sentence-transformers when not available
"""
import numpy as np
import hashlib

class SentenceTransformer:
    def __init__(self, model_name):
        self.model_name = model_name
        print(f"Using fallback SentenceTransformer for {model_name}")
    
    def encode(self, sentences):
        """Create simple hash-based embeddings as fallback"""
        if isinstance(sentences, str):
            sentences = [sentences]
        
        embeddings = []
        for sentence in sentences:
            # Create a simple hash-based embedding
            hash_obj = hashlib.md5(sentence.lower().encode())
            hash_hex = hash_obj.hexdigest()
            
            # Convert hex to numbers and normalize
            embedding = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(len(hash_hex), 64), 2)]
            
            # Pad or truncate to fixed size (384 dimensions like MiniLM)
            while len(embedding) < 384:
                embedding.extend(embedding[:min(384-len(embedding), len(embedding))])
            embedding = embedding[:384]
            
            embeddings.append(embedding)
        
        return np.array(embeddings, dtype=np.float32)
'''
    
    with open(f"{fallback_dir}/sentence_transformers.py", "w") as f:
        f.write(fallback_sentence_transformer)
    
    # Create minimal faiss fallback
    fallback_faiss = '''
"""
Minimal fallback for faiss when not available
"""
import numpy as np

class IndexFlatIP:
    def __init__(self, dimension):
        self.dimension = dimension
        self.vectors = []
        self.is_trained = True
    
    def add(self, vectors):
        """Add vectors to the index"""
        if len(self.vectors) == 0:
            self.vectors = vectors.copy()
        else:
            self.vectors = np.vstack([self.vectors, vectors])
    
    def search(self, query_vectors, k):
        """Simple cosine similarity search"""
        if len(self.vectors) == 0:
            return np.array([[0.0] * k]), np.array([[0] * k])
        
        # Compute cosine similarity
        similarities = np.dot(query_vectors, self.vectors.T)
        
        # Get top k results
        top_k_indices = np.argsort(similarities[0])[::-1][:k]
        top_k_scores = similarities[0][top_k_indices]
        
        return np.array([top_k_scores]), np.array([top_k_indices])

def normalize_L2(vectors):
    """Normalize vectors to unit length"""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    return vectors / norms

def read_index(path):
    """Dummy function for reading index"""
    return IndexFlatIP(384)

def write_index(index, path):
    """Dummy function for writing index"""
    pass
'''
    
    with open(f"{fallback_dir}/faiss.py", "w") as f:
        f.write(fallback_faiss)
    
    print("✅ Fallback implementations created")

def test_imports():
    """Test if critical imports work"""
    print("🧪 Testing imports...")
    
    critical_imports = [
        'flask',
        'flask_cors',
        'flask_sqlalchemy',
        'requests',
        'dotenv',
        'bs4',
        'langdetect'
    ]
    
    optional_imports = [
        'sentence_transformers',
        'faiss',
        'numpy',
        'sklearn'
    ]
    
    working_critical = 0
    working_optional = 0
    
    for module in critical_imports:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            working_critical += 1
        except ImportError:
            print(f"❌ {module} - CRITICAL")
    
    for module in optional_imports:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            working_optional += 1
        except ImportError:
            print(f"⚠️  {module} - will use fallback")
    
    return working_critical, len(critical_imports), working_optional, len(optional_imports)

def main():
    """Main installation function"""
    print("🚀 Regional Shopping AI - Smart Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    is_python_313 = check_python_version()
    
    # Upgrade pip first
    print("📦 Upgrading pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      capture_output=True, timeout=120)
        print("✅ pip upgraded")
    except Exception as e:
        print(f"⚠️  pip upgrade failed: {e}")
    
    # Install core dependencies
    core_success, core_total = install_core_dependencies()
    
    # Install AI dependencies
    ai_success, ai_total = install_ai_dependencies()
    
    # Create fallbacks if needed
    if ai_success < ai_total:
        create_minimal_fallback()
    
    # Test imports
    print("\n" + "=" * 60)
    critical_working, critical_total, optional_working, optional_total = test_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Installation Summary:")
    print(f"   Core dependencies: {core_success}/{core_total}")
    print(f"   AI dependencies: {ai_success}/{ai_total}")
    print(f"   Critical imports working: {critical_working}/{critical_total}")
    print(f"   Optional imports working: {optional_working}/{optional_total}")
    
    if critical_working == critical_total:
        print("🎉 All critical dependencies installed successfully!")
        print("🚀 You can now run: python start_app.py")
        return 0
    else:
        print("❌ Some critical dependencies failed to install")
        print("💡 Try running: pip install flask flask-cors requests python-dotenv beautifulsoup4")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)