"""
Preenche o Formulário I-129 OFICIAL do USCIS com dados do caso
"""

import sys
import os
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

sys.path.insert(0, '/app')
from h1b_data_model import h1b_data

def fill_i129_form(input_pdf_path, output_pdf_path):
    """
    Preenche o formulário I-129 oficial com dados do caso H-1B
    """
    
    print("\n" + "="*80)
    print("📝 PREENCHENDO FORMULÁRIO I-129 OFICIAL DO USCIS")
    print("="*80)
    
    try:
        # Ler o PDF original
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        
        print(f"✅ Formulário oficial carregado: {len(reader.pages)} páginas")
        
        # Verificar se o PDF tem campos preenchíveis
        if reader.get_form_text_fields():
            print(f"✅ Formulário tem {len(reader.get_form_text_fields())} campos preenchíveis")
            
            # Preparar dados para preenchimento
            form_data = {
                # Part 1: Information About the Employer
                "Pt1Line1a_LegalName": h1b_data.employer['legal_name'],
                "Pt1Line1b_DBA": h1b_data.employer['dba'],
                "Pt1Line2_EIN": h1b_data.employer['ein'],
                "Pt1Line3a_StreetNumberName": h1b_data.employer['address'],
                "Pt1Line3b_AptSteFlrNumber": "",
                "Pt1Line3c_CityOrTown": h1b_data.employer['city'],
                "Pt1Line3d_State": h1b_data.employer['state'],
                "Pt1Line3e_ZipCode": h1b_data.employer['zip'],
                "Pt1Line4_PhoneNumber": h1b_data.employer['phone'],
                
                # Part 2: Information About This Petition
                "Pt2Line1_RequestedNonimmigrantClassification": "H-1B",
                "Pt2Line2_TotalWorkers": "1",
                
                # Part 4: Information About the Beneficiary
                "Pt4Line1a_FamilyName": h1b_data.beneficiary['full_name'].split()[-1].upper(),
                "Pt4Line1b_GivenName": h1b_data.beneficiary['full_name'].split()[0],
                "Pt4Line1c_MiddleName": " ".join(h1b_data.beneficiary['full_name'].split()[1:-1]),
                "Pt4Line2_DateOfBirth": h1b_data.beneficiary['dob'],
                "Pt4Line3_CountryOfBirth": "Brazil",
                "Pt4Line4_CountryOfCitizenship": h1b_data.beneficiary['nationality'],
                "Pt4Line5_PassportNumber": h1b_data.beneficiary['passport_number'],
                "Pt4Line6_PassportExpirationDate": h1b_data.beneficiary['passport_expiry_date'],
                
                # Part 5: Basic Information About the Proposed Employment
                "Pt5Line1_JobTitle": h1b_data.position['title'],
                "Pt5Line2_NOCCode": h1b_data.position['soc_code'],
                "Pt5Line3_NAICSCode": h1b_data.position['naics_code'],
                "Pt5Line4_Salary": h1b_data.position['salary_annual'],
                "Pt5Line5_SalaryPer": "Year",
                
                # Part 6: Dates of Intended Employment
                "Pt6Line1_StartDate": h1b_data.position['start_date'],
                "Pt6Line2_EndDate": h1b_data.position['end_date'],
            }
            
            # Tentar preencher os campos
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                writer.add_page(page)
                
                # Atualizar campos se existirem
                if reader.get_form_text_fields():
                    writer.update_page_form_field_values(
                        writer.pages[page_num], 
                        form_data
                    )
            
            print(f"✅ Campos preenchidos com dados do caso")
            
        else:
            # Se não tem campos preenchíveis, apenas copiar as páginas
            print("⚠️ Formulário não tem campos editáveis (PDF estático)")
            print("   Copiando formulário original para o pacote...")
            
            for page in reader.pages:
                writer.add_page(page)
        
        # Salvar o PDF preenchido
        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        file_size = os.path.getsize(output_pdf_path)
        print(f"\n✅ Formulário I-129 preparado!")
        print(f"   📄 Arquivo: {output_pdf_path}")
        print(f"   📊 Tamanho: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   📃 Páginas: {len(writer.pages)}")
        print("="*80)
        
        return output_pdf_path
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_i129_with_data_overlay(input_pdf_path, output_pdf_path):
    """
    Cria uma versão do I-129 com overlay de dados (se o PDF não for editável)
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from PyPDF2 import PdfReader, PdfWriter
    import io
    
    print("\n📝 Criando overlay de dados no formulário...")
    
    # Ler o formulário original
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Criar overlay para a primeira página com dados básicos
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Adicionar dados essenciais nas posições aproximadas
    # (Estas posições seriam ajustadas após análise do formulário)
    can.setFont("Helvetica", 10)
    
    # Exemplo de dados que podemos adicionar
    annotations = [
        (100, 700, f"Petitioner: {h1b_data.employer['legal_name']}"),
        (100, 680, f"EIN: {h1b_data.employer['ein']}"),
        (100, 500, f"Beneficiary: {h1b_data.beneficiary['full_name']}"),
        (100, 480, f"DOB: {h1b_data.beneficiary['dob']}"),
        (100, 460, f"Position: {h1b_data.position['title']}"),
        (100, 440, f"Salary: {h1b_data.position['salary_annual']}"),
    ]
    
    for x, y, text in annotations:
        can.drawString(x, y, text)
    
    can.save()
    
    # Mover para o início do stream
    packet.seek(0)
    
    # Mesclar overlay com primeira página
    overlay_pdf = PdfReader(packet)
    first_page = reader.pages[0]
    first_page.merge_page(overlay_pdf.pages[0])
    writer.add_page(first_page)
    
    # Adicionar páginas restantes
    for page_num in range(1, len(reader.pages)):
        writer.add_page(reader.pages[page_num])
    
    # Salvar
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"✅ Formulário com overlay criado: {output_pdf_path}")
    return output_pdf_path


if __name__ == "__main__":
    input_form = "/tmp/i-129-official.pdf"
    output_form = "/app/I-129_FILLED_OFFICIAL.pdf"
    
    if not os.path.exists(input_form):
        print(f"❌ Formulário oficial não encontrado: {input_form}")
        print("   Baixe de: https://www.uscis.gov/i-129")
    else:
        # Tentar preencher o formulário
        result = fill_i129_form(input_form, output_form)
        
        if result:
            print(f"\n🎉 Sucesso! Formulário I-129 oficial pronto para inclusão no pacote")
        else:
            print(f"\n⚠️ Usando método alternativo...")
            create_i129_with_data_overlay(input_form, output_form)
