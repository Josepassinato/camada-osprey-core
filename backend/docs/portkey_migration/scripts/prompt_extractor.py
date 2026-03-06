"""
Prompt Extractor
Extracts prompts from Python codebase using AST parsing
"""

import ast
import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PromptExtractor:
    """Extract prompts from Python source code"""
    
    def __init__(self, backend_dir: str = None):
        # Auto-detect backend directory
        if backend_dir is None:
            if Path("scripts").exists() and Path("scripts/prompt_extractor.py").exists():
                # Running from backend/
                backend_dir = "."
            else:
                # Running from root
                backend_dir = "backend"
        
        self.backend_dir = Path(backend_dir)
        self.prompts = []
        self.prompt_counter = 1
        
    def extract_all_prompts(self) -> List[Dict[str, Any]]:
        """Extract all prompts from backend directory"""
        logger.info(f"🔍 Scanning {self.backend_dir} for prompts...")
        
        # Find all Python files
        python_files = list(self.backend_dir.rglob("*.py"))
        
        # Exclude certain directories
        excluded = ["__pycache__", ".venv", "venv", "tests", "migrations"]
        python_files = [
            f for f in python_files
            if not any(ex in str(f) for ex in excluded)
        ]
        
        logger.info(f"📁 Found {len(python_files)} Python files to scan")
        
        for file_path in python_files:
            try:
                self._extract_from_file(file_path)
            except Exception as e:
                logger.warning(f"⚠️  Error processing {file_path}: {e}")
        
        logger.info(f"✅ Extracted {len(self.prompts)} prompts")
        return self.prompts
    
    def _extract_from_file(self, file_path: Path):
        """Extract prompts from a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Extract from get_system_prompt methods
            self._extract_system_prompts(tree, file_path, content)
            
            # Extract from inline LLM calls
            self._extract_inline_prompts(tree, file_path, content)
            
        except SyntaxError as e:
            logger.warning(f"⚠️  Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.warning(f"⚠️  Error reading {file_path}: {e}")
    
    def _extract_system_prompts(self, tree: ast.AST, file_path: Path, content: str):
        """Extract prompts from get_system_prompt() methods"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_system_prompt":
                # Get class name if method is in a class
                class_name = self._get_class_name(tree, node)
                
                # Extract prompt text
                prompt_text = self._extract_prompt_text(node, content)
                
                if prompt_text:
                    # Detect variables
                    variables = self._detect_variables(prompt_text)
                    
                    prompt_data = {
                        "id": f"PROMPT_{self.prompt_counter:03d}",
                        "portkey_id": None,
                        "name": f"{class_name or 'Unknown'} System Prompt",
                        "agent": class_name,
                        "location": {
                            "file": str(file_path.relative_to(self.backend_dir.parent)),
                            "line": node.lineno,
                            "function": node.name,
                            "class": class_name
                        },
                        "type": "system",
                        "text": prompt_text[:500] + "..." if len(prompt_text) > 500 else prompt_text,
                        "full_text": prompt_text,
                        "variables": variables,
                        "config": self._infer_config(class_name),
                        "priority": self._determine_priority(class_name, file_path),
                        "status": "not_started",
                        "created_at": None,
                        "migrated_at": None
                    }
                    
                    self.prompts.append(prompt_data)
                    self.prompt_counter += 1
                    logger.debug(f"  📝 Found system prompt in {class_name}")
    
    def _extract_inline_prompts(self, tree: ast.AST, file_path: Path, content: str):
        """Extract prompts from inline LLM calls"""
        for node in ast.walk(tree):
            # Look for messages=[...] patterns
            if isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if keyword.arg == "messages" and isinstance(keyword.value, ast.List):
                        self._process_messages_list(keyword.value, file_path, content, node)
    
    def _process_messages_list(self, messages_node: ast.List, file_path: Path, content: str, call_node: ast.Call):
        """Process a messages list from LLM call"""
        messages = []
        
        for msg_node in messages_node.elts:
            if isinstance(msg_node, ast.Dict):
                msg_dict = {}
                for key, value in zip(msg_node.keys, msg_node.values):
                    if isinstance(key, ast.Constant) and key.value == "role":
                        if isinstance(value, ast.Constant):
                            msg_dict["role"] = value.value
                    elif isinstance(key, ast.Constant) and key.value == "content":
                        # Extract content (could be string, f-string, etc.)
                        content_text = self._extract_node_value(value, content)
                        if content_text:
                            msg_dict["content"] = content_text
                
                if msg_dict:
                    messages.append(msg_dict)
        
        if messages:
            # Create prompt entry
            function_name = self._get_containing_function(call_node)
            
            # Extract system message if present
            system_msg = next((m for m in messages if m.get("role") == "system"), None)
            
            if system_msg:
                prompt_text = system_msg.get("content", "")
                variables = self._detect_variables(prompt_text)
                
                prompt_data = {
                    "id": f"PROMPT_{self.prompt_counter:03d}",
                    "portkey_id": None,
                    "name": f"{function_name or 'Inline'} Prompt",
                    "agent": None,
                    "location": {
                        "file": str(file_path.relative_to(self.backend_dir.parent)),
                        "line": call_node.lineno,
                        "function": function_name,
                        "class": None
                    },
                    "type": "inline",
                    "text": prompt_text[:500] + "..." if len(prompt_text) > 500 else prompt_text,
                    "full_text": prompt_text,
                    "messages": messages,
                    "variables": variables,
                    "config": self._extract_call_config(call_node),
                    "priority": "MEDIUM",
                    "status": "not_started",
                    "created_at": None,
                    "migrated_at": None
                }
                
                self.prompts.append(prompt_data)
                self.prompt_counter += 1
                logger.debug(f"  📝 Found inline prompt in {function_name}")
    
    def _get_class_name(self, tree: ast.AST, node: ast.FunctionDef) -> Optional[str]:
        """Get class name for a method"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for item in parent.body:
                    if item == node:
                        return parent.name
        return None
    
    def _get_containing_function(self, node: ast.AST) -> Optional[str]:
        """Get containing function name (simplified)"""
        # This is a simplified version - in practice, would need parent tracking
        return "unknown_function"
    
    def _extract_prompt_text(self, node: ast.FunctionDef, content: str) -> Optional[str]:
        """Extract prompt text from function body"""
        # Look for return statement with f-string or string
        for item in ast.walk(node):
            if isinstance(item, ast.Return) and item.value:
                return self._extract_node_value(item.value, content)
        return None
    
    def _extract_node_value(self, node: ast.AST, content: str) -> Optional[str]:
        """Extract string value from AST node"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.JoinedStr):
            # F-string - extract template
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(value.value)
                elif isinstance(value, ast.FormattedValue):
                    # Variable placeholder
                    if isinstance(value.value, ast.Name):
                        parts.append("{{" + value.value.id + "}}")
                    elif isinstance(value.value, ast.Attribute):
                        parts.append("{{" + ast.unparse(value.value) + "}}")
                    else:
                        parts.append("{{var}}")
            return "".join(parts)
        return None
    
    def _detect_variables(self, text: str) -> List[Dict[str, Any]]:
        """Detect variables in prompt text"""
        variables = []
        
        # Find f-string style variables: {variable_name}
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        matches = re.findall(pattern, text)
        
        for var_name in set(matches):
            variables.append({
                "name": var_name,
                "type": "str",
                "required": True,
                "default": None
            })
        
        return variables
    
    def _infer_config(self, class_name: Optional[str]) -> Dict[str, Any]:
        """Infer LLM configuration based on agent type"""
        # Default config
        config = {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        if not class_name:
            return config
        
        # Adjust based on agent type
        if "Maria" in class_name:
            config["temperature"] = 0.8
            config["max_tokens"] = 1500
        elif "Validator" in class_name or "Analyzer" in class_name:
            config["temperature"] = 0.3
            config["max_tokens"] = 2000
        elif "Translator" in class_name:
            config["temperature"] = 0.3
            config["max_tokens"] = 1000
        
        return config
    
    def _extract_call_config(self, call_node: ast.Call) -> Dict[str, Any]:
        """Extract configuration from LLM call"""
        config = {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": None
        }
        
        for keyword in call_node.keywords:
            if keyword.arg == "model" and isinstance(keyword.value, ast.Constant):
                config["model"] = keyword.value.value
            elif keyword.arg == "temperature" and isinstance(keyword.value, ast.Constant):
                config["temperature"] = keyword.value.value
            elif keyword.arg == "max_tokens" and isinstance(keyword.value, ast.Constant):
                config["max_tokens"] = keyword.value.value
        
        return config
    
    def _determine_priority(self, class_name: Optional[str], file_path: Path) -> str:
        """Determine migration priority"""
        if not class_name:
            return "MEDIUM"
        
        # High priority agents
        high_priority = ["Maria", "DraPaula", "ImmigrationExpert", "Owl"]
        if any(hp in class_name for hp in high_priority):
            return "HIGH"
        
        # High priority files
        if "server.py" in str(file_path):
            return "HIGH"
        
        return "MEDIUM"
    
    def save_catalog(self, output_file: str = "backend/prompts_catalog.json"):
        """Save extracted prompts to JSON file"""
        catalog = {
            "metadata": {
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "total_prompts": len(self.prompts),
                "backend_dir": str(self.backend_dir)
            },
            "prompts": self.prompts
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved catalog to {output_file}")
        return output_file
    
    def generate_report(self, output_file: str = "backend/PROMPT_EXTRACTION_REPORT.md"):
        """Generate human-readable extraction report"""
        report = f"""# Prompt Extraction Report

**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Prompts Extracted**: {len(self.prompts)}

## Summary by Priority

"""
        
        # Count by priority
        priority_counts = {}
        for prompt in self.prompts:
            priority = prompt.get("priority", "UNKNOWN")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            count = priority_counts.get(priority, 0)
            report += f"- **{priority}**: {count} prompts\n"
        
        report += "\n## Summary by Type\n\n"
        
        # Count by type
        type_counts = {}
        for prompt in self.prompts:
            ptype = prompt.get("type", "unknown")
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        for ptype, count in type_counts.items():
            report += f"- **{ptype}**: {count} prompts\n"
        
        report += "\n## Extracted Prompts\n\n"
        
        # List all prompts
        for prompt in sorted(self.prompts, key=lambda p: p.get("priority", "ZZZ")):
            report += f"### {prompt['id']}: {prompt['name']}\n\n"
            report += f"- **Location**: `{prompt['location']['file']}:{prompt['location']['line']}`\n"
            report += f"- **Type**: {prompt['type']}\n"
            report += f"- **Priority**: {prompt['priority']}\n"
            
            if prompt.get('agent'):
                report += f"- **Agent**: {prompt['agent']}\n"
            
            if prompt.get('variables'):
                report += f"- **Variables**: {', '.join(v['name'] for v in prompt['variables'])}\n"
            
            report += f"- **Config**: Model={prompt['config']['model']}, Temp={prompt['config']['temperature']}\n"
            report += f"\n**Preview**:\n```\n{prompt['text']}\n```\n\n"
            report += "---\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Generated report: {output_file}")
        return output_file


def main():
    """Main extraction function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    extractor = PromptExtractor()
    prompts = extractor.extract_all_prompts()
    
    # Save catalog
    catalog_file = extractor.save_catalog()
    
    # Generate report
    report_file = extractor.generate_report()
    
    print(f"\n✅ Extraction complete!")
    print(f"📊 Total prompts: {len(prompts)}")
    print(f"💾 Catalog: {catalog_file}")
    print(f"📄 Report: {report_file}")


if __name__ == "__main__":
    main()
