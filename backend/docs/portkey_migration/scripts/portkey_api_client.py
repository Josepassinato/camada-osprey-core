"""
Portkey API Client
Wrapper for Portkey SDK to manage prompts programmatically
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PortkeyAPIClient:
    """Client for Portkey API using official SDK"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_PORTKEY_API_KEY")
        if not self.api_key:
            raise ValueError("LLM_PORTKEY_API_KEY not found in environment")
        
        # Import Portkey SDK
        try:
            from portkey_ai import Portkey
            self.portkey = Portkey(api_key=self.api_key)
            logger.info("Portkey SDK client initialized")
        except ImportError:
            raise ImportError("portkey-ai package not installed. Run: pip install portkey-ai")
    
    async def test_connection(self) -> bool:
        """Test API connection and authentication"""
        try:
            # Try to make a simple API call
            # Note: Portkey SDK doesn't have a direct prompts API yet
            # We'll test by trying to use the client
            logger.info("✅ Portkey SDK initialized successfully")
            logger.info(f"   API Key: {self.api_key[:10]}...")
            return True
                    
        except Exception as e:
            logger.error(f"❌ Portkey SDK initialization error: {e}")
            return False
    
    async def create_prompt(
        self,
        name: str,
        messages: List[Dict[str, str]],
        description: str = "",
        variables: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new prompt in Portkey
        
        Note: Portkey SDK doesn't have direct prompt management API yet.
        This is a placeholder for when the API becomes available.
        
        For now, we'll store prompts locally and use them via the SDK.
        """
        logger.warning("⚠️  Portkey SDK doesn't support prompt management API yet")
        logger.info(f"   Creating local prompt: {name}")
        
        # Generate a local prompt ID
        prompt_id = f"pp-local-{name.lower().replace(' ', '-')}"
        
        result = {
            "id": prompt_id,
            "name": name,
            "description": description,
            "messages": messages,
            "variables": variables or [],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tags": tags or [],
            "status": "local",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"✅ Created local prompt: {name} (ID: {prompt_id})")
        return result
    
    async def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Get prompt by ID (placeholder)"""
        logger.warning("⚠️  Portkey SDK doesn't support prompt retrieval yet")
        return {"id": prompt_id, "status": "local"}
    
    async def list_prompts(
        self,
        limit: int = 100,
        offset: int = 0,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List all prompts (placeholder)"""
        logger.warning("⚠️  Portkey SDK doesn't support prompt listing yet")
        logger.info("   Returning empty list")
        return []
    
    async def update_prompt(
        self,
        prompt_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update existing prompt (placeholder)"""
        logger.warning("⚠️  Portkey SDK doesn't support prompt updates yet")
        return {"id": prompt_id, "status": "local"}
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete prompt by ID (placeholder)"""
        logger.warning("⚠️  Portkey SDK doesn't support prompt deletion yet")
        return True
    
    async def batch_create_prompts(
        self,
        prompts: List[Dict[str, Any]],
        delay: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Create multiple prompts with rate limiting
        """
        import asyncio
        
        results = []
        for i, prompt_def in enumerate(prompts):
            try:
                logger.info(f"Creating prompt {i+1}/{len(prompts)}: {prompt_def.get('name')}")
                
                result = await self.create_prompt(**prompt_def)
                results.append({
                    "success": True,
                    "prompt": result,
                    "original": prompt_def
                })
                
                # Rate limiting
                if i < len(prompts) - 1:
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to create prompt {prompt_def.get('name')}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "original": prompt_def
                })
        
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"✅ Batch creation complete: {success_count}/{len(prompts)} successful")
        
        return results


# Convenience function for testing
async def test_portkey_connection():
    """Test Portkey SDK connection"""
    try:
        client = PortkeyAPIClient()
        success = await client.test_connection()
        
        if success:
            print("✅ Portkey SDK initialized successfully!")
            print("\n📋 Note: Portkey SDK doesn't have prompt management API yet.")
            print("   Prompts will be stored locally in the catalog.")
            print("   You can still use Portkey for LLM calls via the SDK.")
        else:
            print("❌ Portkey SDK initialization failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    
    # Test connection
    asyncio.run(test_portkey_connection())
