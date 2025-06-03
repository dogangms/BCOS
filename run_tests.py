#!/usr/bin/env python3
"""
Simple test runner for Step 5 bonus features
"""

if __name__ == "__main__":
    try:
        import test_step5
        print("🧪 Running Step 5 Bonus Features Tests...")
        success = test_step5.run_comprehensive_tests()
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        import traceback
        traceback.print_exc() 