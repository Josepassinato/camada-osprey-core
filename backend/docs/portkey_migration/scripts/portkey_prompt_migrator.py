"""
Portkey Prompt Migrator
Main orchestrator for automated prompt migration to Portkey
"""

import asyncio
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

from prompt_extractor import PromptExtractor
from portkey_api_client import PortkeyAPIClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PortkeyPromptMigrator:
    """Orchestrates the full prompt migration process"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        
        # Determine if we're running from backend/ or root
        if Path("scripts").exists():
            # Running from backend/
            self.catalog_file = Path("prompts_catalog.json")
            self.workplan_file = Path("PROMPT_MIGRATION_WORKPLAN.md")
            self.backend_dir = Path(".")
        else:
            # Running from root
            self.catalog_file = Path("backend/prompts_catalog.json")
            self.workplan_file = Path("backend/PROMPT_MIGRATION_WORKPLAN.md")
            self.backend_dir = Path("backend")
        
        self.extractor = PromptExtractor(backend_dir=str(self.backend_dir))
        self.portkey_client = PortkeyAPIClient()
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    async def run_full_migration(self):
        """Run complete migration process"""
        logger.info("🚀 Starting full prompt migration...")
        
        # Phase 1: Test connection
        logger.info("\n" + "="*60)
        logger.info("PHASE 1: Testing Portkey Connection")
        logger.info("="*60)
        await self.test_connection()
        
        # Phase 2: Extract prompts
        logger.info("\n" + "="*60)
        logger.info("PHASE 2: Extracting Prompts from Codebase")
        logger.info("="*60)
        await self.extract_prompts()
        
        # Phase 3: Create in Portkey
        logger.info("\n" + "="*60)
        logger.info("PHASE 3: Creating Prompts in Portkey")
        logger.info("="*60)
        await self.create_prompts_in_portkey()
        
        # Phase 4: Generate patches
        logger.info("\n" + "="*60)
        logger.info("PHASE 4: Generating Code Migration Patches")
        logger.info("="*60)
        await self.generate_migration_patches()
        
        logger.info("\n✅ Full migration complete!")
        self.print_summary()
    
    async def test_connection(self):
        """Test Portkey API connection"""
        success = await self.portkey_client.test_connection()
        
        if not success:
            raise Exception("❌ Portkey API connection failed. Check your API key.")
        
        # List existing prompts
        existing = await self.portkey_client.list_prompts(limit=10)
        logger.info(f"📋 Found {len(existing)} existing prompts in Portkey")
        
        self.update_workplan_phase(1, "completed")
    
    async def extract_prompts(self):
        """Extract all prompts from codebase"""
        prompts = self.extractor.extract_all_prompts()
        
        # Save catalog
        self.extractor.save_catalog(str(self.catalog_file))
        
        # Generate report (use same directory as catalog)
        report_file = self.catalog_file.parent / "PROMPT_EXTRACTION_REPORT.md"
        self.extractor.generate_report(str(report_file))
        
        logger.info(f"✅ Extracted {len(prompts)} prompts")
        
        # Print summary
        priority_counts = {}
        for prompt in prompts:
            priority = prompt.get("priority", "UNKNOWN")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        logger.info("\n📊 Extraction Summary:")
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            count = priority_counts.get(priority, 0)
            logger.info(f"  {priority}: {count} prompts")
        
        self.update_workplan_phase(2, "completed", extracted=len(prompts))
    
    async def create_prompts_in_portkey(self):
        """Create all prompts in Portkey via API"""
        # Load catalog
        with open(self.catalog_file, 'r') as f:
            catalog = json.load(f)
        
        prompts = catalog.get("prompts", [])
        
        if self.dry_run:
            logger.info(f"🔍 DRY RUN: Would create {len(prompts)} prompts")
            return
        
        # Group by priority
        high_priority = [p for p in prompts if p.get("priority") == "HIGH"]
        medium_priority = [p for p in prompts if p.get("priority") == "MEDIUM"]
        low_priority = [p for p in prompts if p.get("priority") == "LOW"]
        
        logger.info(f"\n📊 Creating prompts by priority:")
        logger.info(f"  HIGH: {len(high_priority)}")
        logger.info(f"  MEDIUM: {len(medium_priority)}")
        logger.info(f"  LOW: {len(low_priority)}")
        
        # Create prompts in batches
        all_results = []
        
        # Batch 1: High priority
        if high_priority:
            logger.info("\n🔥 Creating HIGH priority prompts...")
            results = await self._create_prompt_batch(high_priority)
            all_results.extend(results)
        
        # Batch 2: Medium priority
        if medium_priority:
            logger.info("\n📝 Creating MEDIUM priority prompts...")
            results = await self._create_prompt_batch(medium_priority)
            all_results.extend(results)
        
        # Batch 3: Low priority
        if low_priority:
            logger.info("\n📋 Creating LOW priority prompts...")
            results = await self._create_prompt_batch(low_priority)
            all_results.extend(results)
        
        # Update catalog with Portkey IDs
        self._update_catalog_with_portkey_ids(all_results)
        
        # Generate creation report
        self._generate_creation_report(all_results)
        
        success_count = sum(1 for r in all_results if r["success"])
        logger.info(f"\n✅ Created {success_count}/{len(prompts)} prompts successfully")
        
        self.update_workplan_phase(3, "completed", created=success_count)
    
    async def _create_prompt_batch(self, prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a batch of prompts"""
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"  [{i+1}/{len(prompts)}] Creating: {prompt['name']}")
                
                # Prepare messages
                messages = self._prepare_messages(prompt)
                
                # Prepare variables
                variables = self._prepare_variables(prompt.get("variables", []))
                
                # Create in Portkey
                result = await self.portkey_client.create_prompt(
                    name=prompt["name"],
                    description=f"Migrated from {prompt['location']['file']}",
                    messages=messages,
                    variables=variables,
                    model=prompt["config"].get("model", "gpt-4o"),
                    temperature=prompt["config"].get("temperature", 0.7),
                    max_tokens=prompt["config"].get("max_tokens"),
                    tags=["automated-migration", prompt.get("priority", "MEDIUM").lower()]
                )
                
                results.append({
                    "success": True,
                    "prompt_id": prompt["id"],
                    "portkey_id": result.get("id"),
                    "name": prompt["name"]
                })
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"  ❌ Failed to create {prompt['name']}: {e}")
                results.append({
                    "success": False,
                    "prompt_id": prompt["id"],
                    "name": prompt["name"],
                    "error": str(e)
                })
        
        return results
    
    def _prepare_messages(self, prompt: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for Portkey API"""
        if prompt.get("messages"):
            # Already has messages structure
            return prompt["messages"]
        
        # Create from full_text
        if prompt.get("type") == "system":
            return [
                {
                    "role": "system",
                    "content": prompt.get("full_text", prompt.get("text", ""))
                }
            ]
        
        return [
            {
                "role": "user",
                "content": prompt.get("full_text", prompt.get("text", ""))
            }
        ]
    
    def _prepare_variables(self, variables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare variables for Portkey API"""
        portkey_vars = []
        
        for var in variables:
            portkey_vars.append({
                "name": var["name"],
                "type": "string",  # Portkey uses "string" not "str"
                "required": var.get("required", True),
                "default": var.get("default")
            })
        
        return portkey_vars
    
    def _update_catalog_with_portkey_ids(self, results: List[Dict[str, Any]]):
        """Update catalog with Portkey prompt IDs"""
        # Load catalog
        with open(self.catalog_file, 'r') as f:
            catalog = json.load(f)
        
        # Update prompts with Portkey IDs
        for result in results:
            if result["success"]:
                for prompt in catalog["prompts"]:
                    if prompt["id"] == result["prompt_id"]:
                        prompt["portkey_id"] = result["portkey_id"]
                        prompt["status"] = "created"
                        prompt["created_at"] = datetime.now(timezone.utc).isoformat()
                        break
        
        # Save updated catalog
        with open(self.catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Updated catalog with Portkey IDs")
    
    def _generate_creation_report(self, results: List[Dict[str, Any]]):
        """Generate Portkey creation report"""
        report = f"""# Portkey Prompt Creation Report

**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Prompts**: {len(results)}
**Successful**: {sum(1 for r in results if r['success'])}
**Failed**: {sum(1 for r in results if not r['success'])}

## Successful Creations

"""
        
        for result in results:
            if result["success"]:
                report += f"- ✅ **{result['name']}**\n"
                report += f"  - Prompt ID: `{result['prompt_id']}`\n"
                report += f"  - Portkey ID: `{result['portkey_id']}`\n\n"
        
        if any(not r["success"] for r in results):
            report += "\n## Failed Creations\n\n"
            for result in results:
                if not result["success"]:
                    report += f"- ❌ **{result['name']}**\n"
                    report += f"  - Prompt ID: `{result['prompt_id']}`\n"
                    report += f"  - Error: {result.get('error', 'Unknown')}\n\n"
        
        # Use same directory as catalog
        report_file = self.catalog_file.parent / "PORTKEY_CREATION_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info("📄 Generated creation report")
    
    async def generate_migration_patches(self):
        """Generate code migration patches"""
        # Load catalog with Portkey IDs
        with open(self.catalog_file, 'r') as f:
            catalog = json.load(f)
        
        prompts = catalog.get("prompts", [])
        created_prompts = [p for p in prompts if p.get("portkey_id")]
        
        logger.info(f"📝 Generating migration patches for {len(created_prompts)} prompts")
        
        patches = self._generate_patches(created_prompts)
        
        # Save patches document
        self._save_patches_document(patches)
        
        logger.info(f"✅ Generated {len(patches)} migration patches")
        
        self.update_workplan_phase(4, "completed", patches=len(patches))
    
    def _generate_patches(self, prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate code patches for each prompt"""
        patches = []
        
        for prompt in prompts:
            patch = {
                "prompt_id": prompt["id"],
                "portkey_id": prompt["portkey_id"],
                "name": prompt["name"],
                "location": prompt["location"],
                "before": self._generate_before_code(prompt),
                "after": self._generate_after_code(prompt)
            }
            patches.append(patch)
        
        return patches
    
    def _generate_before_code(self, prompt: Dict[str, Any]) -> str:
        """Generate 'before' code example"""
        if prompt["type"] == "system":
            return f"""# {prompt['location']['file']}:{prompt['location']['line']}

def {prompt['location']['function']}(self) -> str:
    return f\"\"\"
{prompt.get('text', '')[:200]}...
\"\"\"
"""
        else:
            return f"""# {prompt['location']['file']}:{prompt['location']['line']}

messages = [
    {{
        "role": "system",
        "content": "{prompt.get('text', '')[:100]}..."
    }}
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)
"""
    
    def _generate_after_code(self, prompt: Dict[str, Any]) -> str:
        """Generate 'after' code example"""
        variables = prompt.get("variables", [])
        var_dict = ", ".join([f'"{v["name"]}": {v["name"]}' for v in variables])
        
        return f"""# {prompt['location']['file']}:{prompt['location']['line']}
# Migrated to Portkey: {prompt['portkey_id']}

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="{prompt['portkey_id']}",
    variables={{{var_dict}}}
)
"""
    
    def _save_patches_document(self, patches: List[Dict[str, Any]]):
        """Save migration patches document"""
        doc = f"""# Prompt Migration Patches

**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Patches**: {len(patches)}

This document contains code migration patches for all prompts migrated to Portkey.

---

"""
        
        for i, patch in enumerate(patches, 1):
            doc += f"## Patch {i}: {patch['name']}\n\n"
            doc += f"**Prompt ID**: `{patch['prompt_id']}`\n"
            doc += f"**Portkey ID**: `{patch['portkey_id']}`\n"
            doc += f"**Location**: `{patch['location']['file']}:{patch['location']['line']}`\n\n"
            
            doc += "### Before\n\n```python\n"
            doc += patch['before']
            doc += "\n```\n\n"
            
            doc += "### After\n\n```python\n"
            doc += patch['after']
            doc += "\n```\n\n"
            doc += "---\n\n"
        
        # Use same directory as catalog
        patches_file = self.catalog_file.parent / "PROMPT_MIGRATION_PATCHES.md"
        with open(patches_file, 'w') as f:
            f.write(doc)
        
        logger.info("📄 Saved migration patches document")
    
    def update_workplan_phase(self, phase: int, status: str, **metrics):
        """Update workplan document with progress"""
        # This would update the PROMPT_MIGRATION_WORKPLAN.md file
        # For now, just log
        logger.info(f"📊 Phase {phase} {status}: {metrics}")
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        if self.catalog_file.exists():
            with open(self.catalog_file, 'r') as f:
                catalog = json.load(f)
            
            total = len(catalog.get("prompts", []))
            created = sum(1 for p in catalog["prompts"] if p.get("portkey_id"))
            
            print(f"Total Prompts: {total}")
            print(f"Created in Portkey: {created}")
            print(f"Success Rate: {created/total*100:.1f}%")
        
        print("\n📁 Generated Files:")
        print(f"  - {self.catalog_file}")
        extraction_report = self.catalog_file.parent / "PROMPT_EXTRACTION_REPORT.md"
        creation_report = self.catalog_file.parent / "PORTKEY_CREATION_REPORT.md"
        patches_file = self.catalog_file.parent / "PROMPT_MIGRATION_PATCHES.md"
        print(f"  - {extraction_report}")
        print(f"  - {creation_report}")
        print(f"  - {patches_file}")
        print("\n✅ Migration complete!")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Portkey Prompt Migrator")
    parser.add_argument("--full", action="store_true", help="Run full migration")
    parser.add_argument("--extract", action="store_true", help="Extract prompts only")
    parser.add_argument("--create-prompts", action="store_true", help="Create prompts in Portkey")
    parser.add_argument("--generate-patches", action="store_true", help="Generate migration patches")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
    
    args = parser.parse_args()
    
    migrator = PortkeyPromptMigrator(dry_run=args.dry_run)
    
    if args.full:
        await migrator.run_full_migration()
    elif args.extract:
        await migrator.extract_prompts()
    elif args.create_prompts:
        await migrator.create_prompts_in_portkey()
    elif args.generate_patches:
        await migrator.generate_migration_patches()
    else:
        # Default: run full migration
        await migrator.run_full_migration()


if __name__ == "__main__":
    asyncio.run(main())
