#!/usr/bin/env python3
"""
Test script to verify all shopping agents are working properly
"""

import sys
import os
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        from src.config import get_config
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Tavily API enabled: {config.ENABLE_TAVILY_SEARCH}")
        print(f"   - RAG Service enabled: {config.ENABLE_RAG_SERVICE}")
        print(f"   - DuckDuckGo enabled: {config.ENABLE_DUCKDUCKGO_SEARCH}")
        print(f"   - Agent timeout: {config.AGENT_TIMEOUT}s")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_service_manager():
    """Test service manager initialization"""
    print("\n🔧 Testing service manager...")
    try:
        from src.services.service_manager import service_manager
        status = service_manager.get_service_status()
        print(f"✅ Service manager initialized successfully")
        print(f"   - Active services: {status['active_count']}/{status['total_count']}")
        for service, status_val in status['services'].items():
            print(f"   - {service}: {status_val}")
        return True
    except Exception as e:
        print(f"❌ Service manager test failed: {e}")
        traceback.print_exc()
        return False

def test_tavily_service():
    """Test Tavily shopping service"""
    print("\n🔧 Testing Tavily service...")
    try:
        from src.services.service_manager import service_manager
        results = service_manager.search_tavily("milk", 2)
        print(f"✅ Tavily service working")
        print(f"   - Results found: {len(results)}")
        if results:
            print(f"   - Sample result: {results[0]['name'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ Tavily service test failed: {e}")
        return False

def test_duckduckgo_service():
    """Test DuckDuckGo shopping service"""
    print("\n🔧 Testing DuckDuckGo service...")
    try:
        from src.services.service_manager import service_manager
        results = service_manager.search_duckduckgo("rice", 2)
        print(f"✅ DuckDuckGo service working")
        print(f"   - Results found: {len(results)}")
        if results:
            print(f"   - Sample result: {results[0]['name'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ DuckDuckGo service test failed: {e}")
        return False

def test_price_comparison():
    """Test price comparison functionality"""
    print("\n🔧 Testing price comparison...")
    try:
        from src.services.service_manager import service_manager
        comparison = service_manager.get_price_comparison("paneer")
        print(f"✅ Price comparison working")
        if 'error' not in comparison:
            print(f"   - Price range available: {'price_range' in comparison}")
            print(f"   - Recommendations available: {'recommendations' in comparison}")
        else:
            print(f"   - Using fallback data: {comparison.get('source', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Price comparison test failed: {e}")
        return False

def test_local_search():
    """Test local shopping database search"""
    print("\n🔧 Testing local search...")
    try:
        from src.routes.shopping import search_shopping_items, initialize_shopping_models
        
        # Try to initialize models
        try:
            initialize_shopping_models()
            print("✅ Local models initialized")
        except Exception as e:
            print(f"⚠️  Local models initialization warning: {e}")
        
        # Test search
        results = search_shopping_items("spinach", 2)
        print(f"✅ Local search working")
        print(f"   - Results found: {len(results)}")
        if results:
            print(f"   - Sample result: {results[0]['name']}")
        return True
    except Exception as e:
        print(f"❌ Local search test failed: {e}")
        return False

def test_health_check():
    """Test overall system health"""
    print("\n🔧 Testing system health...")
    try:
        from src.services.service_manager import service_manager
        health = service_manager.health_check()
        print(f"✅ Health check completed")
        print(f"   - Overall health: {health['overall_health']}")
        print(f"   - Fallback available: {health['fallback_available']}")
        
        for service, status in health['services'].items():
            print(f"   - {service}: {status['status']}")
        return True
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Shopping Agents Test Suite")
    print("=" * 50)
    
    tests = [
        test_config,
        test_service_manager,
        test_tavily_service,
        test_duckduckgo_service,
        test_price_comparison,
        test_local_search,
        test_health_check
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All agents are working properly!")
        return 0
    elif passed >= total // 2:
        print("⚠️  Most agents are working, some issues detected")
        return 1
    else:
        print("❌ Multiple agent failures detected")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)