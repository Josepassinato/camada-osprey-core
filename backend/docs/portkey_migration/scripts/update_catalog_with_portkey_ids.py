"""
Update prompts_catalog.json with Portkey IDs after manual creation
"""

import json
from pathlib import Path
from datetime import datetime, timezone

def update_catalog():
    """Interactive script to update catalog with Portkey IDs"""
    
    # Load catalog
    catalog_file = Path("prompts_catalog.json")
    if not catalog_file.exists():
        catalog_file = Path("../prompts_catalog.json")
    
    with open(catalog_file, 'r') as f:
        catalog = json.load(f)
    
    print("=" * 60)
    print("Portkey ID Update Tool")
    print("=" * 60)
    print(f"\nTotal prompts: {len(catalog['prompts'])}")
    print("\nEnter Portkey IDs for each prompt.")
    print("Press Enter to skip a prompt.")
    print("Type 'quit' to exit and save.\n")
    
    updated_count = 0
    
    for i, prompt in enumerate(catalog['prompts'], 1):
        print(f"\n[{i}/{len(catalog['prompts'])}] {prompt['name']}")
        print(f"   ID: {prompt['id']}")
        print(f"   Location: {prompt['location']['file']}:{prompt['location']['line']}")
        print(f"   Current Portkey ID: {prompt.get('portkey_id', 'NOT SET')}")
        
        portkey_id = input(f"   Enter Portkey ID (or press Enter to skip): ").strip()
        
        if portkey_id.lower() == 'quit':
            print("\n⚠️  Exiting early...")
            break
        
        if portkey_id:
            prompt['portkey_id'] = portkey_id
            prompt['status'] = 'created'
            prompt['created_at'] = datetime.now(timezone.utc).isoformat()
            updated_count += 1
            print(f"   ✅ Updated with ID: {portkey_id}")
    
    # Save updated catalog
    with open(catalog_file, 'w') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Updated {updated_count} prompts")
    print(f"💾 Saved to {catalog_file}")
    print(f"{'=' * 60}")
    
    # Show summary
    total = len(catalog['prompts'])
    created = sum(1 for p in catalog['prompts'] if p.get('portkey_id') and not p['portkey_id'].startswith('pp-local-'))
    pending = total - created
    
    print(f"\nSummary:")
    print(f"  Total: {total}")
    print(f"  Created in Portkey: {created}")
    print(f"  Pending: {pending}")
    print(f"  Progress: {created/total*100:.1f}%")

if __name__ == "__main__":
    try:
        update_catalog()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
