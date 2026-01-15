"""
Generate CSV and JSON files for manual Portkey prompt creation
"""

import json
import csv
from pathlib import Path

def generate_csv_export():
    """Generate CSV file for manual prompt creation"""
    # Load catalog
    catalog_file = Path("prompts_catalog.json")
    if not catalog_file.exists():
        catalog_file = Path("../prompts_catalog.json")
    
    with open(catalog_file, 'r') as f:
        catalog = json.load(f)
    
    prompts = catalog['prompts']
    
    # Create CSV
    output_file = catalog_file.parent / "prompts_for_portkey_import.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'ID', 'Name', 'Type', 'Priority', 'Agent', 
            'File', 'Line', 'Model', 'Temperature', 'Max Tokens',
            'Variables', 'Prompt Preview', 'Full Prompt'
        ])
        
        # Data
        for p in prompts:
            variables = ', '.join([v['name'] for v in p.get('variables', [])])
            text_preview = p.get('text', '')[:200].replace('\n', ' ')
            full_text = p.get('full_text', p.get('text', ''))
            
            writer.writerow([
                p['id'],
                p['name'],
                p['type'],
                p['priority'],
                p.get('agent', ''),
                p['location']['file'],
                p['location']['line'],
                p['config']['model'],
                p['config']['temperature'],
                p['config'].get('max_tokens', ''),
                variables,
                text_preview,
                full_text
            ])
    
    print(f"✅ Created {output_file}")
    return output_file

def generate_json_export():
    """Generate JSON file for potential bulk import"""
    # Load catalog
    catalog_file = Path("prompts_catalog.json")
    if not catalog_file.exists():
        catalog_file = Path("../prompts_catalog.json")
    
    with open(catalog_file, 'r') as f:
        catalog = json.load(f)
    
    prompts = catalog['prompts']
    
    # Create simplified JSON for import
    import_data = {
        "version": "1.0",
        "total_prompts": len(prompts),
        "prompts": []
    }
    
    for p in prompts:
        import_data["prompts"].append({
            "name": p['name'],
            "description": f"Migrated from {p['location']['file']}:{p['location']['line']}",
            "messages": p.get('messages', [
                {
                    "role": "system" if p['type'] == "system" else "user",
                    "content": p.get('full_text', p.get('text', ''))
                }
            ]),
            "variables": p.get('variables', []),
            "model": p['config']['model'],
            "temperature": p['config']['temperature'],
            "max_tokens": p['config'].get('max_tokens'),
            "tags": [p['priority'].lower(), p['type']],
            "metadata": {
                "original_id": p['id'],
                "agent": p.get('agent'),
                "location": p['location']
            }
        })
    
    output_file = catalog_file.parent / "prompts_for_portkey_import.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(import_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {output_file}")
    return output_file

if __name__ == "__main__":
    print("🔄 Generating Portkey import files...")
    csv_file = generate_csv_export()
    json_file = generate_json_export()
    print(f"\n✅ Generated 2 files:")
    print(f"   - {csv_file}")
    print(f"   - {json_file}")
