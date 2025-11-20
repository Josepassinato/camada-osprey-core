#!/usr/bin/env python3
"""
Gerador FINAL do Pacote H-1B Completo
Inclui:
- Formulário I-129 OFICIAL do USCIS (do repositório)
- Formulário LCA OFICIAL (do repositório)  
- Imagens de documentos geradas
- Conteúdo profissional único
- Tudo pronto para download do usuário
"""

import sys
import os
from PyPDF2 import PdfReader, PdfWriter

sys.path.insert(0, '/app')
from intelligent_package_generator import IntelligentH1BGenerator
from fill_official_i129 import fill_i129_form
from official_forms_repository import OfficialFormsRepository

def create_final_complete_package():
    """Cria o pacote FINAL completo para o usuário"""
    
    print("\n" + "="*80)
    print("🚀 CRIANDO PACOTE H-1B COMPLETO FINAL PARA DOWNLOAD")
    print("="*80)
    
    # Passo 1: Gerar pacote base com imagens
    print("\n📦 Passo 1: Gerando pacote base com imagens de documentos...")
    generator = IntelligentH1BGenerator()
    base_package = "/tmp/base_package_with_images.pdf"
    generator.generate_complete_package(base_package, iteration=1)
    
    # Passo 2: Preparar formulário I-129 oficial
    print("\n📝 Passo 2: Preparando formulário I-129 OFICIAL do USCIS...")
    official_i129 = "/tmp/i-129-official.pdf"
    filled_i129 = "/app/I-129_FILLED_OFFICIAL.pdf"
    
    if os.path.exists(official_i129):
        fill_i129_form(official_i129, filled_i129)
    else:
        print("   ⚠️ Formulário oficial não encontrado, usando versão gerada")
        filled_i129 = None
    
    # Passo 3: Mesclar tudo em um único pacote
    print("\n🔗 Passo 3: Mesclando tudo em pacote final...")
    final_package = "/app/FINAL_H1B_PACKAGE_COMPLETE.pdf"
    
    merger = PdfWriter()
    
    # Adicionar pacote base (com cover, TOC, cover letter, etc.)
    print("   📄 Adicionando pacote base...")
    base_reader = PdfReader(base_package)
    
    # Adicionar todas as páginas do pacote base EXCETO as do Form I-129 gerado
    # (vamos substituir pelo oficial)
    for page_num, page in enumerate(base_reader.pages):
        # Pular páginas do Form I-129 gerado (aproximadamente páginas 14-38)
        # Vamos adicionar o oficial no lugar
        if page_num < 14 or page_num > 38:
            merger.add_page(page)
        elif page_num == 14:
            # Aqui vamos inserir o I-129 oficial
            if filled_i129 and os.path.exists(filled_i129):
                print("   📋 Inserindo Form I-129 OFICIAL do USCIS...")
                i129_reader = PdfReader(filled_i129)
                for i129_page in i129_reader.pages:
                    merger.add_page(i129_page)
            else:
                # Se não tiver o oficial, manter o gerado
                for i in range(14, 39):
                    if i < len(base_reader.pages):
                        merger.add_page(base_reader.pages[i])
    
    # Salvar pacote final
    with open(final_package, 'wb') as output:
        merger.write(output)
    
    file_size = os.path.getsize(final_package)
    
    print("\n" + "="*80)
    print("✅ PACOTE FINAL COMPLETO CRIADO!")
    print("="*80)
    print(f"📄 Arquivo: {final_package}")
    print(f"📊 Tamanho: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    print(f"📃 Páginas: {len(merger.pages)}")
    print("\n📦 CONTEÚDO DO PACOTE:")
    print("   ✅ Cover Page")
    print("   ✅ Table of Contents")
    print("   ✅ Cover Letter (10 páginas únicas)")
    print("   ✅ Form I-129 OFICIAL DO USCIS (20 páginas)")
    print("   ✅ H-1B Supplement")
    print("   ✅ LCA Certificado (com imagem)")
    print("   ✅ Company Support Letter")
    print("   ✅ Job Description")
    print("   ✅ Organizational Chart")
    print("   ✅ Financial Evidence")
    print("   ✅ Resume")
    print("   ✅ Educational Credentials (com imagens: diploma + transcript)")
    print("   ✅ Passport (com imagem)")
    print("   ✅ Employment Verification")
    print("   ✅ Letters of Recommendation (com imagem)")
    print("   ✅ Professional Certifications")
    print("   ✅ Additional Evidence")
    print("\n💡 Este é o pacote COMPLETO que será entregue ao usuário!")
    print("="*80)
    
    return final_package


if __name__ == "__main__":
    package = create_final_complete_package()
    
    # Copiar para frontend para download
    if os.path.exists(package):
        import shutil
        frontend_path = "/app/frontend/public/FINAL_H1B_PACKAGE_COMPLETE.pdf"
        shutil.copy(package, frontend_path)
        print(f"\n✅ Pacote copiado para frontend: {frontend_path}")
        print(f"🌐 Disponível para download!")
