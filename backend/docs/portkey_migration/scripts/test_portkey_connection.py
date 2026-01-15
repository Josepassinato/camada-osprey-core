"""
Test Portkey API Connection
Simple script to verify Portkey API is accessible
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.portkey_api_client import PortkeyAPIClient


async def main():
    """Test Portkey connection"""
    print("🔍 Testing Portkey API Connection...\n")
    
    try:
        # Initialize client
        print("1️⃣  Initializing Portkey client...")
        client = PortkeyAPIClient()
        print("   ✅ Client initialized\n")
        
        # Test connection
        print("2️⃣  Testing API connection...")
        success = await client.test_connection()
        
        if not success:
            print("   ❌ Connection failed!")
            return False
        
        print("   ✅ Connection successful!\n")
        
        # List existing prompts
        print("3️⃣  Listing existing prompts...")
        prompts = await client.list_prompts(limit=10)
        print(f"   ✅ Found {len(prompts)} prompts\n")
        
        if prompts:
            print("📋 Existing Prompts:")
            for i, prompt in enumerate(prompts[:5], 1):
                print(f"   {i}. {prompt.get('name')} (ID: {prompt.get('id')})")
        else:
            print("   (No prompts found - this is normal for a new account)")
        
        print("\n✅ All tests passed!")
        print("\n🚀 Ready to run prompt migration!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check that LLM_PORTKEY_API_KEY is set in backend/.env")
        print("   2. Verify your API key is valid at https://app.portkey.ai")
        print("   3. Ensure you have internet connectivity")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
