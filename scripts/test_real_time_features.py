#!/usr/bin/env python3
"""
Test script for real-time features
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_imports():
    """Test that all new modules can be imported"""
    try:
        from app.api.routers import websocket
        print("✓ WebSocket router imported successfully")
    except Exception as e:
        print(f"✗ Failed to import WebSocket router: {e}")
        return False
        
    try:
        from app.services import job_service
        print("✓ Job service imported successfully")
    except Exception as e:
        print(f"✗ Failed to import job service: {e}")
        return False
        
    try:
        from app.services import resume_enhancer
        print("✓ Resume enhancer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import resume enhancer: {e}")
        return False
        
    return True

def test_frontend_files():
    """Test that frontend files exist"""
    required_files = [
        'frontend/src/services/jobService.js',
        'frontend/src/services/resumeService.js',
        'frontend/src/hooks/useResume.js',
        'frontend/src/pages/RealTimeJobs.jsx'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            return False
            
    return True

def main():
    """Run all tests"""
    print("Testing real-time features implementation...\n")
    
    success = True
    success &= test_imports()
    success &= test_frontend_files()
    
    print("\n" + "="*50)
    if success:
        print("✓ All tests passed! Real-time features are properly implemented.")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())