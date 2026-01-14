"""
Quick import verification for Maria agent migration
Run this to verify all imports work correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)
print(f"Project root: {project_root}")

def test_imports():
    """Test all Maria agent imports"""
    print("Testing Maria agent imports...")
    
    try:
        # Test package import
        print("✓ Testing package import...")
        from backend.agents.maria import MariaAgent, maria
        print("  ✅ Package imports successful")
        
        # Test agent module
        print("✓ Testing agent module...")
        from backend.agents.maria.agent import MariaAgent as MA
        print("  ✅ Agent module imports successful")
        
        # Test gemini_chat module
        print("✓ Testing gemini_chat module...")
        from backend.agents.maria.gemini_chat import MariaGeminiChat, maria_gemini
        print("  ✅ Gemini chat module imports successful")
        
        # Test api module
        print("✓ Testing api module...")
        from backend.agents.maria.api import router
        print("  ✅ API module imports successful")
        
        # Test voice module
        print("✓ Testing voice module...")
        from backend.agents.maria.voice import MariaVoiceService, maria_voice
        print("  ✅ Voice module imports successful")
        
        # Test whatsapp module
        print("✓ Testing whatsapp module...")
        from backend.agents.maria.whatsapp import MariaWhatsAppService, maria_whatsapp
        print("  ✅ WhatsApp module imports successful")
        
        # Verify BaseAgent inheritance
        print("✓ Verifying BaseAgent inheritance...")
        from backend.agents.base import BaseAgent
        assert issubclass(MariaAgent, BaseAgent), "MariaAgent should inherit from BaseAgent"
        print("  ✅ MariaAgent correctly inherits from BaseAgent")
        
        # Verify LLMClient usage
        print("✓ Verifying LLMClient integration...")
        agent = MariaAgent()
        assert hasattr(agent, 'llm_client'), "MariaAgent should have llm_client attribute"
        assert hasattr(agent, '_call_llm'), "MariaAgent should have _call_llm method"
        print("  ✅ LLMClient integration verified")
        
        print("\n" + "="*60)
        print("🎉 ALL IMPORTS SUCCESSFUL!")
        print("="*60)
        print("\nMaria agent migration completed successfully!")
        print("- Package structure: ✅")
        print("- Module imports: ✅")
        print("- BaseAgent inheritance: ✅")
        print("- LLMClient integration: ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
