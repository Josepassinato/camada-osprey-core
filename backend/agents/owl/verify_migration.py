"""
Simple verification script for Owl agent migration
Run from backend directory: python3 -m agents.owl.verify_migration
"""

def verify_migration():
    """Verify the migration was successful"""
    print("=" * 60)
    print("Owl Agent Migration Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check 1: File exists
    import os
    agent_file = os.path.join(os.path.dirname(__file__), 'agent.py')
    if os.path.exists(agent_file):
        checks.append(("✅", "agent.py file exists"))
    else:
        checks.append(("❌", "agent.py file missing"))
    
    # Check 2: __init__.py exists
    init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    if os.path.exists(init_file):
        checks.append(("✅", "__init__.py file exists"))
    else:
        checks.append(("❌", "__init__.py file missing"))
    
    # Check 3: Check for emergent imports
    with open(agent_file, 'r') as f:
        content = f.read()
        if 'emergentintegrations' not in content.lower():
            checks.append(("✅", "No emergentintegrations imports"))
        else:
            checks.append(("❌", "Still has emergentintegrations imports"))
        
        if 'EMERGENT_LLM_KEY' not in content:
            checks.append(("✅", "No EMERGENT_LLM_KEY references"))
        else:
            checks.append(("❌", "Still has EMERGENT_LLM_KEY references"))
    
    # Check 4: Check for BaseAgent inheritance
    if 'class IntelligentOwlAgent(BaseAgent):' in content:
        checks.append(("✅", "Inherits from BaseAgent"))
    else:
        checks.append(("❌", "Does not inherit from BaseAgent"))
    
    # Check 5: Check for LLM client imports
    if 'from ..base import BaseAgent' in content:
        checks.append(("✅", "Imports BaseAgent"))
    else:
        checks.append(("❌", "Missing BaseAgent import"))
    
    if 'from ...llm.portkey_client import LLMClient' in content:
        checks.append(("✅", "Imports LLMClient"))
    else:
        checks.append(("❌", "Missing LLMClient import"))
    
    if 'from ...llm.types import ChatMessage, MessageRole' in content:
        checks.append(("✅", "Imports LLM types"))
    else:
        checks.append(("❌", "Missing LLM types import"))
    
    # Check 6: Check for process method
    if 'async def process(self, input_data: Dict[str, Any])' in content:
        checks.append(("✅", "Has process() method"))
    else:
        checks.append(("❌", "Missing process() method"))
    
    # Check 7: Check for _call_llm usage
    if 'await self._call_llm(' in content:
        checks.append(("✅", "Uses _call_llm() helper"))
    else:
        checks.append(("❌", "Not using _call_llm() helper"))
    
    # Check 8: Check migration summary exists
    summary_file = os.path.join(os.path.dirname(__file__), 'MIGRATION_SUMMARY.md')
    if os.path.exists(summary_file):
        checks.append(("✅", "MIGRATION_SUMMARY.md exists"))
    else:
        checks.append(("❌", "MIGRATION_SUMMARY.md missing"))
    
    # Print results
    print("Migration Checks:")
    print("-" * 60)
    for status, message in checks:
        print(f"{status} {message}")
    
    print()
    print("=" * 60)
    
    # Summary
    passed = sum(1 for status, _ in checks if status == "✅")
    total = len(checks)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("=" * 60)
        return True
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total} passed)")
        print("=" * 60)
        return False


if __name__ == "__main__":
    import sys
    success = verify_migration()
    sys.exit(0 if success else 1)
