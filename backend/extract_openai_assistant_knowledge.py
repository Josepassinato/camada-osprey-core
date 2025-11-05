"""
Script to EXTRACT knowledge from OpenAI Assistant
This ONLY reads data, doesn't modify anything

Run this to backup all knowledge from Dra. Paula's OpenAI Assistant
"""

import os
import json
import asyncio
from datetime import datetime
from openai import AsyncOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def extract_assistant_knowledge(assistant_id: str = "asst_kkyn65SQFfkloH4SalOZfwwh"):
    """
    Extract all knowledge from OpenAI Assistant
    
    This function:
    1. Reads assistant configuration
    2. Downloads instructions
    3. Lists attached files (if any)
    4. Downloads file contents
    5. Saves everything locally
    
    IMPORTANT: This is READ-ONLY, doesn't modify anything in OpenAI
    """
    
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        logger.error("❌ OPENAI_API_KEY not found")
        return False
    
    try:
        client = AsyncOpenAI(api_key=openai_key)
        
        logger.info(f"🔍 Extracting knowledge from Assistant: {assistant_id}")
        
        # 1. Get assistant details
        logger.info("📥 Retrieving assistant configuration...")
        assistant = await client.beta.assistants.retrieve(assistant_id)
        
        # 2. Save assistant configuration
        assistant_config = {
            "id": assistant.id,
            "name": assistant.name,
            "description": assistant.description,
            "model": assistant.model,
            "instructions": assistant.instructions,
            "tools": [tool.model_dump() if hasattr(tool, 'model_dump') else str(tool) for tool in assistant.tools],
            "file_ids": assistant.file_ids if hasattr(assistant, 'file_ids') else [],
            "metadata": assistant.metadata,
            "extracted_at": datetime.utcnow().isoformat()
        }
        
        # Save configuration
        config_filename = f"dra_paula_assistant_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"/app/backend/{config_filename}", "w", encoding="utf-8") as f:
            json.dump(assistant_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Configuration saved to: {config_filename}")
        
        # 3. Save instructions separately
        if assistant.instructions:
            instructions_filename = f"dra_paula_instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(f"/app/backend/{instructions_filename}", "w", encoding="utf-8") as f:
                f.write(assistant.instructions)
            logger.info(f"✅ Instructions saved to: {instructions_filename}")
            logger.info(f"📝 Instructions preview: {assistant.instructions[:200]}...")
        else:
            logger.warning("⚠️ No instructions found in assistant")
        
        # 4. List and download files (if any)
        if hasattr(assistant, 'file_ids') and assistant.file_ids:
            logger.info(f"📁 Found {len(assistant.file_ids)} files attached")
            
            files_info = []
            for i, file_id in enumerate(assistant.file_ids, 1):
                try:
                    logger.info(f"📥 Downloading file {i}/{len(assistant.file_ids)}: {file_id}")
                    
                    # Get file info
                    file_info = await client.files.retrieve(file_id)
                    
                    # Download file content
                    file_content = await client.files.content(file_id)
                    
                    # Save file
                    safe_filename = f"dra_paula_file_{i}_{file_info.filename}"
                    with open(f"/app/backend/{safe_filename}", "wb") as f:
                        f.write(file_content.read())
                    
                    files_info.append({
                        "file_id": file_id,
                        "filename": file_info.filename,
                        "purpose": file_info.purpose,
                        "bytes": file_info.bytes,
                        "created_at": file_info.created_at,
                        "saved_as": safe_filename
                    })
                    
                    logger.info(f"✅ File saved as: {safe_filename}")
                    
                except Exception as e:
                    logger.error(f"❌ Error downloading file {file_id}: {str(e)}")
                    files_info.append({
                        "file_id": file_id,
                        "error": str(e)
                    })
            
            # Save files manifest
            manifest_filename = f"dra_paula_files_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(f"/app/backend/{manifest_filename}", "w", encoding="utf-8") as f:
                json.dump(files_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Files manifest saved to: {manifest_filename}")
        else:
            logger.info("ℹ️ No files attached to this assistant")
        
        # 5. Generate summary report
        summary = {
            "extraction_successful": True,
            "assistant_id": assistant_id,
            "assistant_name": assistant.name,
            "model_used": assistant.model,
            "has_instructions": bool(assistant.instructions),
            "instructions_length": len(assistant.instructions) if assistant.instructions else 0,
            "files_count": len(assistant.file_ids) if hasattr(assistant, 'file_ids') else 0,
            "extracted_at": datetime.utcnow().isoformat(),
            "files_saved": [
                config_filename,
                instructions_filename if assistant.instructions else None,
            ]
        }
        
        summary_filename = f"dra_paula_extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"/app/backend/{summary_filename}", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Summary saved to: {summary_filename}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 EXTRACTION SUMMARY")
        print("="*60)
        print(f"✅ Assistant ID: {assistant_id}")
        print(f"✅ Assistant Name: {assistant.name}")
        print(f"✅ Model: {assistant.model}")
        print(f"✅ Instructions: {'Yes' if assistant.instructions else 'No'} ({len(assistant.instructions) if assistant.instructions else 0} chars)")
        print(f"✅ Files: {len(assistant.file_ids) if hasattr(assistant, 'file_ids') else 0}")
        print("\n📁 Files saved in /app/backend/:")
        print(f"   - {config_filename}")
        if assistant.instructions:
            print(f"   - {instructions_filename}")
        print(f"   - {summary_filename}")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error extracting assistant knowledge: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main execution"""
    print("\n🔧 OpenAI Assistant Knowledge Extractor")
    print("="*60)
    print("This tool extracts knowledge from Dra. Paula's OpenAI Assistant")
    print("READ-ONLY operation - doesn't modify anything")
    print("="*60)
    
    success = await extract_assistant_knowledge()
    
    if success:
        print("\n✅ Extraction completed successfully!")
        print("\nNext steps:")
        print("1. Review extracted files in /app/backend/")
        print("2. Integrate any new knowledge into dra_paula_knowledge_base.py")
        print("3. Test gemini_dra_paula_agent.py with extracted knowledge")
    else:
        print("\n❌ Extraction failed. Check logs for details.")


if __name__ == "__main__":
    asyncio.run(main())
