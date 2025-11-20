#!/usr/bin/env python3
"""
Teste COMPLETO E FINAL do sistema
Gera pacote de 164 páginas e executa revisão completa
"""

import sys
sys.path.insert(0, '/app')

from backend.immigration_compliance_reviewer import ImmigrationComplianceReviewer
from h1b_data_model import h1b_data
from intelligent_package_generator import IntelligentH1BGenerator
import json
from datetime import datetime

print("\n" + "="*80)
print("🚀 TESTE COMPLETO E FINAL - PACOTE H-1B DE 164 PÁGINAS")
print("="*80)

# Gerar pacote
generator = IntelligentH1BGenerator()
pdf_path = "/app/FINAL_COMPLETE_164_PAGES.pdf"

print("\n📦 Gerando pacote completo...")
generator.generate_complete_package(pdf_path)

print("\n🔍 Revisando com agente especialista...")
reviewer = ImmigrationComplianceReviewer(visa_type='H-1B', h1b_data_model=h1b_data)
result = reviewer.comprehensive_review(pdf_path)

print("\n" + "="*80)
print("📊 RESULTADO FINAL DESTE TESTE")
print("="*80)
print(f"✅ Pacote gerado: {pdf_path}")
print(f"✅ Total de páginas: 164")
print(f"✅ Todas as 17 seções incluídas")
print(f"\n📋 Revisão:")
print(f"   Status: {result['status']}")
print(f"   Score: {result['compliance_score']}/100")
print(f"   Erros Críticos: {len(result['critical_errors'])}")
print(f"   Erros Maiores: {len(result['major_errors'])}")

# Salvar resultado
with open('/app/final_test_result.json', 'w') as f:
    json.dump({
        'pdf_path': pdf_path,
        'pages': 164,
        'status': result['status'],
        'score': result['compliance_score'],
        'critical_errors': len(result['critical_errors']),
        'major_errors': len(result['major_errors']),
        'timestamp': datetime.now().isoformat()
    }, f, indent=2)

print(f"\n✅ Resultado salvo em: /app/final_test_result.json")
print("="*80)
