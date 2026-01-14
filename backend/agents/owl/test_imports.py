"""
Test script to verify Owl agent imports work correctly after migration
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def test_imports():
    """Test that all imports work correctly"""
    print("Testing Owl agent imports...")
    
    try:
        # Test package import
        from agents.owl import IntelligentOwlAgent
        print("✅ Package import successful: from agents.owl import IntelligentOwlAgent")
        
        # Test direct import
        from agents.owl.agent import IntelligentOwlAgent as OwlAgent
        print("✅ Direct import successful: from agents.owl.agent import IntelligentOwlAgent")
        
        # Test that both imports reference the same class
        assert IntelligentOwlAgent is OwlAgent
        print("✅ Both imports reference the same class")
        
        # Test instantiation
        owl = IntelligentOwlAgent()
        print(f"✅ Agent instantiation successful: {owl}")
        
        # Test that it inherits from BaseAgent
        from agents.base import BaseAgent
        assert isinstance(owl, BaseAgent)
        print("✅ Agent correctly inherits from BaseAgent")
        
        # Test that it has the required methods
        assert hasattr(owl, 'process')
        assert hasattr(owl, '_call_llm')
        assert hasattr(owl, 'get_metrics')
        print("✅ Agent has required BaseAgent methods")
        
        # Test that old attributes are removed
        assert not hasattr(owl, 'ai_client')
        print("✅ Old ai_client attribute removed")
        
        # Test that new attributes exist
        assert hasattr(owl, 'llm_client')
        assert hasattr(owl, 'agent_name')
        assert owl.agent_name == "owl_agent"
        print("✅ New LLM client attributes present")
        
        print("\n🎉 All import tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic_functionality():
    """Test basic agent functionality"""
    print("\nTesting basic Owl agent functionality...")
    
    try:
        from agents.owl import IntelligentOwlAgent
        
        owl = IntelligentOwlAgent()
        
        # Test process method with start_session action
        result = await owl.process({
            "action": "start_session",
            "case_id": "test_case_123",
            "visa_type": "H-1B",
            "language": "pt"
        })
        
        assert "session_id" in result
        assert "visa_type" in result
        assert result["visa_type"] == "H-1B"
        print("✅ start_session action works")
        
        # Test that field guides are loaded
        assert len(owl.field_guides) > 0
        print(f"✅ Field guides loaded: {len(owl.field_guides)} guides")
        
        # Test metrics
        metrics = owl.get_metrics()
        assert "total_calls" in metrics
        print("✅ Metrics collection works")
        
        print("\n🎉 All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Owl Agent Migration Verification")
    print("=" * 60)
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test basic functionality
        functionality_ok = asyncio.run(test_basic_functionality())
        
        if functionality_ok:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED - Migration successful!")
            print("=" * 60)
            sys.exit(0)
    
    print("\n" + "=" * 60)
    print("❌ TESTS FAILED - Please review errors above")
    print("=" * 60)
    sys.exit(1)
