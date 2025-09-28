# Script to replace all OpenAI calls with EmergentIntegrations in server.py

import os
import re

def fix_openai_calls(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove old openai imports
    content = re.sub(r'import openai\n', '', content)
    content = re.sub(r'from openai import.*\n', '', content)
    
    # Add emergentintegrations import after other imports
    if 'from emergentintegrations.llm.chat import LlmChat, UserMessage' not in content:
        # Find the last import line
        import_lines = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                import_lines.append(i)
        
        if import_lines:
            last_import_idx = max(import_lines)
            lines.insert(last_import_idx + 1, 'from emergentintegrations.llm.chat import LlmChat, UserMessage')
            content = '\n'.join(lines)
    
    # Replace OpenAI call patterns with EmergentIntegrations
    # Pattern 1: Basic chat completion
    openai_pattern = r'''response = openai\.chat\.completions\.create\(
            model="([^"]+)",
            messages=\[
                \{
                    "role": "system",\s*
                    "content": "([^"]*)"
                \},
                \{"role": "user", "content": ([^}]+)\}
            \],
            temperature=([0-9.]+),
            max_tokens=(\d+)
        \)
        
        # Parse AI response
        ai_response = response\.choices\[0\]\.message\.content\.strip\(\)'''
    
    # Simple replacement pattern for single system/user message
    def replace_simple_openai(match):
        model = match.group(1)
        system_msg = match.group(2)
        user_content = match.group(3)
        temp = match.group(4)
        max_tokens = match.group(5)
        
        # Map model names
        model_mapping = {
            "gpt-4": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-4-turbo": "gpt-4o"
        }
        mapped_model = model_mapping.get(model, "gpt-4o")
        
        return f'''# Call LLM via emergentintegrations
        chat = LlmChat(
            api_key="sk-emergent-aE5F536B80dFf0bA6F",
            session_id=f"chat_{{uuid.uuid4().hex[:8]}}",
            system_message="{system_msg}"
        ).with_model("openai", "{mapped_model}")
        
        user_message = UserMessage(text={user_content})
        ai_response = await chat.send_message(user_message)'''
    
    # Apply replacements
    content = re.sub(openai_pattern, replace_simple_openai, content, flags=re.MULTILINE | re.DOTALL)
    
    # Manual replacements for specific patterns that might not match the general pattern
    replacements = [
        # Chat endpoint
        (r'''response = openai\.chat\.completions\.create\(
            model="gpt-4",
            messages=messages,
            temperature=0\.7,
            max_tokens=1000,
            stream=False
        \)
        
        ai_response = response\.choices\[0\]\.message\.content''', 
         '''# Call LLM via emergentintegrations
        chat = LlmChat(
            api_key="sk-emergent-aE5F536B80dFf0bA6F",
            session_id=f"chat_{uuid.uuid4().hex[:8]}",
            system_message="You are a helpful assistant for immigration applications."
        ).with_model("openai", "gpt-4o")
        
        # Convert messages to last user message (simplified for now)
        last_user_msg = ""
        for msg in messages:
            if msg["role"] == "user":
                last_user_msg = msg["content"]
        
        user_message = UserMessage(text=last_user_msg)
        ai_response = await chat.send_message(user_message)'''),
        
        # Document analysis
        (r'''response = openai\.chat\.completions\.create\(
            model="gpt-4",
            messages=\[
                \{
                    "role": "system",
                    "content": "([^"]*)"
                \},
                \{
                    "role": "user", 
                    "content": analysis_prompt
                \}
            \],
            temperature=0\.1,
            max_tokens=1000
        \)
        
        ai_response = response\.choices\[0\]\.message\.content\.strip\(\)''',
         '''# Call LLM via emergentintegrations for document analysis
        chat = LlmChat(
            api_key="sk-emergent-aE5F536B80dFf0bA6F",
            session_id=f"doc_analysis_{uuid.uuid4().hex[:8]}",
            system_message="\\1"
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=analysis_prompt)
        ai_response = await chat.send_message(user_message)'''),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("OpenAI calls replaced with EmergentIntegrations")

if __name__ == "__main__":
    fix_openai_calls("/app/backend/server.py")