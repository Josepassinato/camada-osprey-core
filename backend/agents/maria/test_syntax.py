"""
Syntax verification for Maria agent migration
Tests that all files have correct Python syntax
"""

import py_compile
import sys
import os

def test_syntax():
    """Test Python syntax for all Maria modules"""
    print("Testing Maria agent module syntax...")
    
    base_path = os.path.dirname(__file__)
    files_to_test = [
        '__init__.py',
        'agent.py',
        'api.py',
        'gemini_chat.py',
        'voice.py',
        'whatsapp.py'
    ]
    
    all_passed = True
    
    for filename in files_to_test:
        filepath = os.path.join(base_path, filename)
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} - syntax OK")
        except py_compile.PyCompileError as e:
            print(f"  ❌ {filename} - syntax error: {e}")
            all_passed = False
    
    if all_passed:
        print("\n" + "="*60)
        print("🎉 ALL SYNTAX CHECKS PASSED!")
        print("="*60)
        print("\nMaria agent files have correct Python syntax:")
        print("- __init__.py: ✅")
        print("- agent.py: ✅")
        print("- api.py: ✅")
        print("- gemini_chat.py: ✅")
        print("- voice.py: ✅")
        print("- whatsapp.py: ✅")
        return True
    else:
        print("\n❌ Some files have syntax errors")
        return False

if __name__ == "__main__":
    success = test_syntax()
    sys.exit(0 if success else 1)
