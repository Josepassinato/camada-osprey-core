#!/usr/bin/env python3
"""
Compara os dois pacotes H-1B: antigo (repetitivo) vs novo (profissional)
"""

import sys
sys.path.insert(0, '/app')
from h1b_data_model import h1b_data
from backend.advanced_immigration_reviewer import AdvancedImmigrationReviewerAgent
import pdfplumber

print("="*80)
print("📊 COMPARAÇÃO DE PACOTES H-1B")
print("="*80)

# Criar revisor
reviewer = AdvancedImmigrationReviewerAgent(h1b_data)

# Pacotes para comparar
packages = [
    ("PACOTE ANTIGO (REPETITIVO)", "/app/CONSISTENT_H1B_PACKAGE_FERNANDA_SANTOS.pdf"),
    ("PACOTE NOVO (PROFISSIONAL)", "/app/PROFESSIONAL_H1B_PACKAGE_FERNANDA_SANTOS.pdf"),
]

results = []

for name, path in packages:
    print(f"\n{'='*80}")
    print(f"Analisando: {name}")
    print(f"{'='*80}")
    
    # Análise detalhada do conteúdo
    with pdfplumber.open(path) as pdf:
        num_pages = len(pdf.pages)
        
        # Amostrar 5 páginas para verificar unicidade de conteúdo
        sample_pages = [10, 30, 50, 70, 90]
        page_contents = []
        
        for page_num in sample_pages:
            if page_num < num_pages:
                text = pdf.pages[page_num].extract_text() or ""
                # Pegar primeiras 300 caracteres
                snippet = text[:300].replace('\n', ' ')
                page_contents.append((page_num + 1, snippet))
        
        print(f"\n📄 Amostra de conteúdo (primeiras 300 chars de 5 páginas):")
        for page_num, snippet in page_contents:
            print(f"\nPágina {page_num}:")
            print(f"  {snippet}...")
    
    # Revisar pacote
    result = reviewer.review_package(path)
    results.append((name, result))

# Comparação final
print("\n" + "="*80)
print("📊 COMPARAÇÃO FINAL")
print("="*80)

for name, result in results:
    print(f"\n{name}:")
    print(f"  Status: {result['status']}")
    print(f"  Score: {result['score']}/100")
    print(f"  Erros: {len(result['errors'])}")
    print(f"  Avisos: {len(result['warnings'])}")
    
    if result['details']:
        print(f"  Total de páginas: {result['details'].get('total_pages', 'N/A')}")
        print(f"  Páginas duplicadas: {result['details'].get('duplicate_pages', 'N/A')} ({result['details'].get('duplicate_percentage', 0):.1f}%)")
        print(f"  Páginas com conteúdo genérico: {result['details'].get('generic_content_pages', 'N/A')}")

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)

old_score = results[0][1]['score']
new_score = results[1][1]['score']
improvement = new_score - old_score

if improvement > 0:
    print(f"✅ MELHORIA SIGNIFICATIVA: Score aumentou de {old_score} para {new_score} (+{improvement} pontos)")
else:
    print(f"⚠️ Ambos os pacotes precisam de melhorias adicionais")

print("\nOBSERVAÇÃO: Pacotes de imigração reais terão alguma similaridade entre páginas")
print("pois os mesmos dados (nome, salário, datas) aparecem em múltiplas seções.")
print("O importante é que as seções narrativas principais (Cover Letter, Form I-129)")
print("tenham conteúdo profissional e contextual único.")
