#!/usr/bin/env python3
"""
Gerador de Imagens Simuladas para Pacote B-2
Cria imagens realistas de documentos: passaporte, I-94, fotos, etc.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import io

class B2ImageGenerator:
    """Gerador de imagens simuladas para documentos B-2"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path('/app/frontend/public/temp_images')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_passport_photo(self, applicant_data: dict) -> Path:
        """
        Cria uma foto simulada estilo passaporte
        """
        # Criar imagem 2x2 polegadas (600x600 px a 300 DPI)
        img = Image.new('RGB', (600, 600), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Simular fundo azul claro
        draw.rectangle([0, 0, 600, 600], fill='#e8f4f8')
        
        # Simular silhueta de pessoa (círculo para cabeça, retângulo para ombros)
        # Cabeça
        draw.ellipse([200, 150, 400, 350], fill='#d4a574', outline='#c19463')
        
        # Ombros/pescoço
        draw.rectangle([220, 320, 380, 500], fill='#4a5568')
        draw.polygon([220, 320, 380, 320, 420, 500, 180, 500], fill='#4a5568')
        
        # Adicionar texto "SIMULATED PASSPORT PHOTO"
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((300, 550), "SIMULATED IMAGE", fill='#666', anchor='mm', font=font)
        
        # Salvar
        output_path = self.output_dir / 'passport_photo.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_passport_biopage(self, applicant_data: dict) -> Path:
        """
        Cria simulação da página biográfica do passaporte
        """
        # Criar imagem tamanho passaporte (1200x800 px)
        img = Image.new('RGB', (1200, 800), color='white')
        draw = ImageDraw.Draw(img)
        
        # Fundo com padrão
        draw.rectangle([0, 0, 1200, 800], fill='#f8f9fa')
        
        # Header brasileiro
        draw.rectangle([0, 0, 1200, 80], fill='#009b3a')
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            title_font = label_font = data_font = ImageFont.load_default()
        
        # Título
        draw.text((600, 40), "REPÚBLICA FEDERATIVA DO BRASIL", fill='white', anchor='mm', font=title_font)
        
        # Foto (placeholder)
        draw.rectangle([50, 120, 350, 520], fill='#e8f4f8', outline='#666', width=2)
        draw.text((200, 320), "PHOTO", fill='#999', anchor='mm', font=title_font)
        
        # Dados do passaporte
        y_pos = 120
        x_label = 400
        x_data = 600
        line_height = 50
        
        fields = [
            ("Type/Tipo", "P"),
            ("Country Code/País", "BRA"),
            ("Passport No./Passaporte", applicant_data.get('passport_number', 'BR789456123')),
            ("Surname/Sobrenome", applicant_data.get('family_name', 'RODRIGUES COSTA')),
            ("Given Names/Nome", applicant_data.get('given_name', 'MARIA HELENA')),
            ("Nationality/Nacionalidade", "BRAZILIAN"),
            ("Date of Birth/Data Nasc.", applicant_data.get('dob_formatted', '15 APR/ABR 1965')),
            ("Sex/Sexo", applicant_data.get('gender', 'F')),
            ("Place of Birth/Local Nasc.", f"{applicant_data.get('pob_city', 'Belo Horizonte')}, {applicant_data.get('pob_country', 'BRA')}"),
            ("Date of Issue/Emissão", applicant_data.get('passport_issue_date', '10 MAR/MAR 2019')),
            ("Date of Expiry/Validade", applicant_data.get('passport_expiry_date', '09 MAR/MAR 2029')),
        ]
        
        for label, value in fields:
            draw.text((x_label, y_pos), label, fill='#555', font=label_font)
            draw.text((x_data, y_pos + 25), value, fill='#000', font=data_font)
            y_pos += line_height
        
        # Machine Readable Zone (MRZ) at bottom
        draw.rectangle([0, 720, 1200, 800], fill='#e0e0e0')
        mrz_font = ImageFont.load_default()
        mrz_line1 = f"P<BRA{applicant_data.get('family_name', 'RODRIGUES COSTA').replace(' ', '<')}<<{applicant_data.get('given_name', 'MARIA HELENA').replace(' ', '<')}"
        mrz_line2 = f"{applicant_data.get('passport_number', 'BR789456123')}BRA6504159F2903095<<<<<<<<<<<<<<<0"
        
        draw.text((50, 735), mrz_line1[:44], fill='#000', font=mrz_font)
        draw.text((50, 760), mrz_line2[:44], fill='#000', font=mrz_font)
        
        # Watermark
        draw.text((600, 400), "SIMULATED DOCUMENT", fill='#ddd', anchor='mm', font=title_font)
        
        # Salvar
        output_path = self.output_dir / 'passport_biopage.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_i94_form(self, applicant_data: dict, i94_data: dict) -> Path:
        """
        Cria simulação visual do formulário I-94
        """
        # Criar imagem tamanho carta (2550x3300 px a 300 DPI = 8.5x11")
        img = Image.new('RGB', (2550, 3300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            section_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            title_font = section_font = label_font = data_font = ImageFont.load_default()
        
        # Header
        draw.rectangle([0, 0, 2550, 200], fill='#1a365d')
        draw.text((1275, 100), "U.S. CUSTOMS AND BORDER PROTECTION", fill='white', anchor='mm', font=title_font)
        
        # Título do formulário
        draw.rectangle([0, 200, 2550, 350], fill='#2c5282')
        draw.text((1275, 275), "I-94 ARRIVAL/DEPARTURE RECORD", fill='white', anchor='mm', font=section_font)
        
        # Instruções
        y_pos = 400
        draw.text((100, y_pos), "This form must be completed by all persons except U.S. Citizens, returning resident aliens,", 
                 fill='#333', font=label_font)
        y_pos += 40
        draw.text((100, y_pos), "aliens with immigrant visas, and Canadian Citizens visiting or in transit.",
                 fill='#333', font=label_font)
        
        # Campos do formulário
        y_pos = 550
        x_label = 150
        x_data = 800
        field_height = 100
        
        fields = [
            ("1. Family Name (Surname)", applicant_data.get('family_name', 'RODRIGUES COSTA')),
            ("2. First (Given) Name", applicant_data.get('given_name', 'MARIA HELENA')),
            ("3. Birth Date (DD/MM/YYYY)", applicant_data.get('dob_formatted', '15/04/1965')),
            ("4. Country of Citizenship", applicant_data.get('nationality', 'BRAZIL')),
            ("5. Gender", "Female" if applicant_data.get('gender') == 'F' else 'Male'),
            ("6. Passport Number", applicant_data.get('passport_number', 'BR789456123')),
            ("7. Passport Issuing Country", applicant_data.get('passport_country', 'BRAZIL')),
            ("8. Airline and Flight Number", i94_data.get('arrival_airline', 'American Airlines AA 904')),
            ("9. Country Where You Boarded", i94_data.get('departure_country', 'Brazil')),
            ("10. U.S. Address (Street)", applicant_data.get('us_address', '1234 Palm Avenue, Apt 15B')),
            ("     City and State", f"{applicant_data.get('us_city', 'Miami')}, {applicant_data.get('us_state', 'FL')} {applicant_data.get('us_zip', '33139')}"),
        ]
        
        for label, value in fields:
            # Label
            draw.text((x_label, y_pos), label, fill='#2d3748', font=label_font)
            
            # Campo (caixa)
            draw.rectangle([x_label, y_pos + 40, 2400, y_pos + 90], 
                          fill='#f7fafc', outline='#4a5568', width=2)
            
            # Valor
            draw.text((x_label + 20, y_pos + 55), value, fill='#000', font=data_font)
            
            y_pos += field_height
        
        # Seção de admissão (preenchida pelo CBP)
        y_pos += 50
        draw.rectangle([50, y_pos, 2500, y_pos + 450], outline='#e53e3e', width=4, fill='#fff5f5')
        
        draw.text((1275, y_pos + 50), "FOR OFFICIAL USE ONLY - COMPLETED BY U.S. CUSTOMS AND BORDER PROTECTION", 
                 fill='#c53030', anchor='mm', font=section_font)
        
        cbp_y = y_pos + 120
        cbp_fields = [
            ("Admission Number", i94_data.get('i94_number', '94123456789012')),
            ("Class of Admission", i94_data.get('visa_type', 'B-2')),
            ("Date of Admission", i94_data.get('arrival_date', '12/15/2024')),
            ("Admit Until Date", i94_data.get('admit_until', '06/13/2025')),
            ("Port of Entry", i94_data.get('arrival_port', 'Miami International Airport (MIA)')),
        ]
        
        for label, value in cbp_fields:
            draw.text((x_label, cbp_y), f"{label}:", fill='#2d3748', font=label_font)
            draw.rectangle([x_label, cbp_y + 40, 2400, cbp_y + 85], 
                          fill='white', outline='#4a5568', width=2)
            draw.text((x_label + 20, cbp_y + 52), value, fill='#c53030', font=data_font)
            cbp_y += 90
        
        # Rodapé
        y_pos = 3150
        draw.rectangle([0, y_pos, 2550, 3300], fill='#f7fafc')
        draw.text((1275, y_pos + 50), "THIS IS A SIMULATED I-94 FOR DOCUMENTATION PURPOSES", 
                 fill='#999', anchor='mm', font=section_font)
        draw.text((1275, y_pos + 100), "Official I-94 records are maintained electronically at i94.cbp.dhs.gov", 
                 fill='#666', anchor='mm', font=label_font)
        
        # Salvar
        output_path = self.output_dir / 'i94_record.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_bank_statement(self, applicant_data: dict, bank_data: dict, month: str) -> Path:
        """
        Cria extrato bancário simulado
        """
        img = Image.new('RGB', (2550, 3300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
            section_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            title_font = section_font = label_font = data_font = ImageFont.load_default()
        
        # Header do banco
        draw.rectangle([0, 0, 2550, 250], fill='#ffcc00')
        draw.text((1275, 125), "BANCO DO BRASIL", fill='#003399', anchor='mm', font=title_font)
        
        # Informações da conta
        y_pos = 300
        draw.text((100, y_pos), f"Account Holder: {applicant_data.get('full_name', 'MARIA HELENA RODRIGUES COSTA')}", 
                 fill='#000', font=data_font)
        y_pos += 60
        draw.text((100, y_pos), f"Account Number: {bank_data.get('account_number', '12345-6')}", 
                 fill='#000', font=data_font)
        y_pos += 60
        draw.text((100, y_pos), f"Statement Period: {month}", 
                 fill='#000', font=data_font)
        
        # Resumo
        y_pos += 120
        draw.rectangle([50, y_pos, 2500, y_pos + 250], fill='#f0f0f0', outline='#666', width=2)
        
        summary_y = y_pos + 30
        draw.text((100, summary_y), "ACCOUNT SUMMARY", fill='#003399', font=section_font)
        summary_y += 70
        
        draw.text((100, summary_y), f"Opening Balance:", fill='#000', font=label_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('opening_balance', '482,500.00')}", 
                 fill='#000', font=data_font, anchor='rm')
        summary_y += 50
        
        draw.text((100, summary_y), f"Total Credits:", fill='#000', font=label_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('credits', '8,500.00')}", 
                 fill='#006600', font=data_font, anchor='rm')
        summary_y += 50
        
        draw.text((100, summary_y), f"Total Debits:", fill='#000', font=label_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('debits', '6,000.00')}", 
                 fill='#cc0000', font=data_font, anchor='rm')
        summary_y += 50
        
        draw.rectangle([100, summary_y, 2400, summary_y + 2], fill='#003399')
        summary_y += 20
        
        draw.text((100, summary_y), f"CLOSING BALANCE:", fill='#003399', font=section_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('closing_balance', '485,000.00')}", 
                 fill='#003399', font=title_font, anchor='rm')
        
        # Transações
        y_pos += 350
        draw.text((100, y_pos), "TRANSACTIONS", fill='#003399', font=section_font)
        y_pos += 70
        
        # Header da tabela
        draw.rectangle([50, y_pos, 2500, y_pos + 50], fill='#003399')
        draw.text((100, y_pos + 15), "Date", fill='white', font=label_font)
        draw.text((500, y_pos + 15), "Description", fill='white', font=label_font)
        draw.text((1800, y_pos + 15), "Amount", fill='white', font=label_font)
        draw.text((2200, y_pos + 15), "Balance", fill='white', font=label_font)
        
        # Transações simuladas
        transactions = [
            ("01/03/2025", "PENSION DEPOSIT - INSS", "+8,500.00", "482,500.00"),
            ("05/03/2025", "SUPERMARKET - EXTRA", "-850.00", "481,650.00"),
            ("10/03/2025", "PHARMACY - DROGASIL", "-120.00", "481,530.00"),
            ("15/03/2025", "UTILITIES - CEMIG", "-380.00", "481,150.00"),
            ("20/03/2025", "RESTAURANT - GRILL", "-150.00", "481,000.00"),
            ("25/03/2025", "TRANSFER IN", "+4,000.00", "485,000.00"),
        ]
        
        y_pos += 50
        for date, desc, amount, balance in transactions:
            y_pos += 45
            color = '#006600' if '+' in amount else '#000'
            
            draw.text((100, y_pos), date, fill='#000', font=label_font)
            draw.text((500, y_pos), desc, fill='#000', font=label_font)
            draw.text((1800, y_pos), amount, fill=color, font=data_font)
            draw.text((2200, y_pos), balance, fill='#000', font=data_font)
            
            # Linha divisória
            if y_pos < 3000:
                draw.rectangle([50, y_pos + 40, 2500, y_pos + 41], fill='#ddd')
        
        # Rodapé
        y_pos = 3200
        draw.text((1275, y_pos), "THIS IS A SIMULATED BANK STATEMENT FOR DOCUMENTATION PURPOSES", 
                 fill='#999', anchor='mm', font=label_font)
        
        # Salvar
        output_path = self.output_dir / f'bank_statement_{month.replace(" ", "_")}.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path


if __name__ == '__main__':
    """Teste do gerador"""
    from b2_extension_data_model import b2_extension_case
    
    print("\n🖼️  GERANDO IMAGENS SIMULADAS PARA B-2 PACKAGE")
    print("=" * 60)
    
    generator = B2ImageGenerator()
    
    print("\n1. Gerando foto do passaporte...")
    photo = generator.create_passport_photo(b2_extension_case.applicant)
    print(f"   ✅ {photo}")
    
    print("\n2. Gerando página biográfica do passaporte...")
    biopage = generator.create_passport_biopage(b2_extension_case.applicant)
    print(f"   ✅ {biopage}")
    
    print("\n3. Gerando formulário I-94...")
    i94 = generator.create_i94_form(b2_extension_case.applicant, b2_extension_case.current_status)
    print(f"   ✅ {i94}")
    
    print("\n4. Gerando extrato bancário...")
    bank_data = {
        'account_number': '12345-6',
        'opening_balance': '482,500.00',
        'credits': '8,500.00',
        'debits': '6,000.00',
        'closing_balance': '485,000.00'
    }
    statement = generator.create_bank_statement(b2_extension_case.applicant, bank_data, "March 2025")
    print(f"   ✅ {statement}")
    
    print("\n✅ TODAS AS IMAGENS GERADAS COM SUCESSO!")
    print("=" * 60)
