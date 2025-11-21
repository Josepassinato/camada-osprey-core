#!/usr/bin/env python3
"""
Script para aplicar todas as correções de segurança nos endpoints admin
"""

import re

# Lista de todos os endpoints admin que precisam ser protegidos
ADMIN_ENDPOINTS = [
    {
        "pattern": r'@api_router\.post\("/admin/visa-updates/\{update_id\}/reject"\)\nasync def reject_visa_update\(update_id: str, request: Request\):',
        "replacement": '@api_router.post("/admin/visa-updates/{update_id}/reject")\nasync def reject_visa_update(update_id: str, request: Request, admin = Depends(require_admin)):'
    },
    {
        "pattern": r'@api_router\.post\("/admin/visa-updates/run-manual-scan"\)\nasync def run_manual_visa_scan\(\):',
        "replacement": '@api_router.post("/admin/visa-updates/run-manual-scan")\nasync def run_manual_visa_scan(admin = Depends(require_admin)):'
    },
    {
        "pattern": r'@api_router\.get\("/admin/visa-updates/history"\)\nasync def get_visa_updates_history\(',
        "replacement": '@api_router.get("/admin/visa-updates/history")\nasync def get_visa_updates_history(admin = Depends(require_admin),'
    },
    {
        "pattern": r'@api_router\.get\("/admin/notifications"\)\nasync def get_admin_notifications\(\):',
        "replacement": '@api_router.get("/admin/notifications")\nasync def get_admin_notifications(admin = Depends(require_admin)):'
    },
    {
        "pattern": r'@api_router\.put\("/admin/notifications/\{notification_id\}/read"\)\nasync def mark_notification_read\(notification_id: str\):',
        "replacement": '@api_router.put("/admin/notifications/{notification_id}/read")\nasync def mark_notification_read(notification_id: str, admin = Depends(require_admin)):'
    },
    {
        "pattern": r'@api_router\.post\("/admin/knowledge-base/upload"\)\nasync def upload_knowledge_base_document\(',
        "replacement": '@api_router.post("/admin/knowledge-base/upload")\nasync def upload_knowledge_base_document(admin = Depends(require_admin),'
    },
    {
        "pattern": r'@api_router\.get\("/admin/knowledge-base/list"\)\nasync def list_knowledge_base_documents\(',
        "replacement": '@api_router.get("/admin/knowledge-base/list")\nasync def list_knowledge_base_documents(admin = Depends(require_admin),'
    },
    {
        "pattern": r'@api_router\.delete\("/admin/knowledge-base/\{document_id\}"\)\nasync def delete_knowledge_base_document\(document_id: str\):',
        "replacement": '@api_router.delete("/admin/knowledge-base/{document_id}")\nasync def delete_knowledge_base_document(document_id: str, admin = Depends(require_admin)):'
    }
]

def apply_patches():
    """Aplica todos os patches de segurança"""
    
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    original_content = content
    patches_applied = 0
    
    for patch in ADMIN_ENDPOINTS:
        if re.search(patch['pattern'], content):
            content = re.sub(patch['pattern'], patch['replacement'], content)
            patches_applied += 1
            print(f"✅ Patch aplicado: {patch['pattern'][:50]}...")
    
    if content != original_content:
        with open('/app/backend/server.py', 'w') as f:
            f.write(content)
        print(f"\n✅ {patches_applied} patches aplicados com sucesso!")
    else:
        print("\n⚠️ Nenhuma mudança necessária.")

if __name__ == '__main__':
    apply_patches()
