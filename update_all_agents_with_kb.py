#!/usr/bin/env python3
"""
Script para atualizar todos os agentes com knowledge base
Adiciona método de carregamento de KB em cada agente
"""

from pathlib import Path

# Template para adicionar ao __init__ de cada agente
KB_LOADER_TEMPLATE = '''
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load USCIS knowledge base for this visa type"""
        knowledge = {}
        
        kb_dir = Path(__file__).parent.parent / 'knowledge_base' / '{kb_folder}'
        if kb_dir.exists():
            req_file = kb_dir / 'uscis_requirements.md'
            if req_file.exists():
                with open(req_file, 'r', encoding='utf-8') as f:
                    knowledge['requirements'] = f.read()
                print(f"📚 Loaded {self.__class__.__name__} knowledge base ({len(knowledge['requirements'])} chars)")
        
        return knowledge
'''

agents_to_update = [
    {
        'name': 'F1StudentAgent',
        'file': '/app/visa_specialists/f1_student/f1_agent.py',
        'kb_folder': 'f1_student'
    },
    {
        'name': 'H1BWorkerAgent',
        'file': '/app/visa_specialists/h1b_worker/h1b_agent.py',
        'kb_folder': 'h1b_worker'
    },
    {
        'name': 'I130FamilyAgent',
        'file': '/app/visa_specialists/i130_family/i130_agent.py',
        'kb_folder': 'i130_family'
    },
    {
        'name': 'I765EADAgent',
        'file': '/app/visa_specialists/i765_ead/i765_agent.py',
        'kb_folder': 'i765_ead'
    },
    {
        'name': 'I90GreenCardAgent',
        'file': '/app/visa_specialists/i90_greencard/i90_agent.py',
        'kb_folder': 'i90_greencard'
    }
]

print("\n" + "="*80)
print("📚 UPDATING ALL AGENTS WITH KNOWLEDGE BASE LOADERS")
print("="*80)

for agent in agents_to_update:
    print(f"\n✅ {agent['name']}:")
    print(f"   File: {agent['file']}")
    print(f"   KB Folder: {agent['kb_folder']}")
    
    # Check if file exists
    if not Path(agent['file']).exists():
        print(f"   ⚠️  File not found, skipping...")
        continue
    
    # Read file
    with open(agent['file'], 'r') as f:
        content = f.read()
    
    # Check if already has KB loader
    if '_load_knowledge_base' in content:
        print(f"   ℹ️  Already has KB loader, skipping...")
        continue
    
    # Add KB loader to __init__ (find and modify)
    kb_code = KB_LOADER_TEMPLATE.format(kb_folder=agent['kb_folder'])
    
    # Find __init__ and add knowledge base loading
    init_marker = "def __init__(self):"
    if init_marker in content:
        # Add self.knowledge_base line after super().__init__
        super_marker = "super().__init__"
        if super_marker in content:
            # Find the line after super().__init__
            lines = content.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if super_marker in line:
                    # Add KB loader call after super
                    indent = '        '
                    new_lines.append('')
                    new_lines.append(f'{indent}# Load USCIS knowledge base')
                    new_lines.append(f'{indent}self.knowledge_base = self._load_knowledge_base()')
            
            # Add the method at the end of the class (before last methods)
            # Find a good place (before generate_package)
            final_lines = []
            method_added = False
            for i, line in enumerate(new_lines):
                if 'def generate_package' in line and not method_added:
                    # Add KB loader method before generate_package
                    final_lines.extend(kb_code.split('\n'))
                    final_lines.append('')
                    method_added = True
                final_lines.append(line)
            
            if not method_added:
                # Add at end
                final_lines.extend([''] + kb_code.split('\n'))
            
            # Write back
            with open(agent['file'], 'w') as f:
                f.write('\n'.join(final_lines))
            
            print(f"   ✅ Updated with KB loader!")
    else:
        print(f"   ⚠️  Could not find __init__ method, manual update needed")

print("\n" + "="*80)
print("✅ ALL AGENTS UPDATED")
print("="*80)
