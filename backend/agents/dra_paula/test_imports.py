"""
Test script to verify Dra. Paula agent imports work correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all imports work correctly"""
    print("Testing Dra. Paula agent imports...")
    print(f"Project root: {project_root}")
    
    try:
        # Test package import
        import backend.agents.dra_paula as dra_paula_pkg
        print("✅ Package import successful")
        
        # Test individual class imports
        from backend.agents.dra_paula import DraPaulaGeminiAgent
        print("✅ DraPaulaGeminiAgent import successful")
        
        from backend.agents.dra_paula import HybridDraPaulaAgent
        print("✅ HybridDraPaulaAgent import successful")
        
        from backend.agents.dra_paula import DraPaulaKnowledgeBase
        print("✅ DraPaulaKnowledgeBase import successful")
        
        from backend.agents.dra_paula import dra_paula_knowledge
        print("✅ dra_paula_knowledge import successful")
        
        # Test that classes are properly defined
        assert hasattr(DraPaulaGeminiAgent, 'consult'), "DraPaulaGeminiAgent missing consult method"
        assert hasattr(DraPaulaGeminiAgent, 'process'), "DraPaulaGeminiAgent missing process method"
        print("✅ DraPaulaGeminiAgent has required methods")
        
        assert hasattr(HybridDraPaulaAgent, 'consult'), "HybridDraPaulaAgent missing consult method"
        assert hasattr(HybridDraPaulaAgent, 'process'), "HybridDraPaulaAgent missing process method"
        print("✅ HybridDraPaulaAgent has required methods")
        
        assert hasattr(DraPaulaKnowledgeBase, 'get_visa_specific_knowledge'), "DraPaulaKnowledgeBase missing method"
        print("✅ DraPaulaKnowledgeBase has required methods")
        
        # Test BaseAgent inheritance
        from backend.agents.base import BaseAgent
        assert issubclass(DraPaulaGeminiAgent, BaseAgent), "DraPaulaGeminiAgent doesn't inherit from BaseAgent"
        assert issubclass(HybridDraPaulaAgent, BaseAgent), "HybridDraPaulaAgent doesn't inherit from BaseAgent"
        print("✅ Both agents inherit from BaseAgent")
        
        # Test knowledge base instance
        assert isinstance(dra_paula_knowledge, DraPaulaKnowledgeBase), "dra_paula_knowledge is not an instance"
        print("✅ dra_paula_knowledge is properly instantiated")
        
        print("\n🎉 All import tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except AssertionError as e:
        print(f"❌ Assertion error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
