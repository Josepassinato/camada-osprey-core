#!/usr/bin/env python3
"""
Gerador de Imagens Simuladas para Pacote F-1
Cria imagens realistas de documentos: passaporte, I-20, fotos, transcripts, etc.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class F1ImageGenerator:
    """Gerador de imagens simuladas para documentos F-1"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path('/app/frontend/public/temp_images')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_passport_photo(self, applicant_data: dict) -> Path:
        """Cria foto estilo passaporte 2x2"""
        img = Image.new('RGB', (600, 600), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Fundo branco/cinza claro
        draw.rectangle([0, 0, 600, 600], fill='#f8f9fa')
        
        # Silhueta masculina (cabeça)
        draw.ellipse([200, 120, 400, 320], fill='#d4a574', outline='#c19463', width=2)
        
        # Cabelo
        draw.ellipse([200, 100, 400, 250], fill='#2c1810')
        
        # Pescoço/ombros
        draw.rectangle([220, 300, 380, 480], fill='#1e3a5f')
        draw.polygon([220, 300, 380, 300, 440, 500, 160, 500], fill='#1e3a5f')
        
        # Adicionar texto
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = small_font = ImageFont.load_default()
        
        draw.text((300, 550), "PASSPORT PHOTO", fill='#666', anchor='mm', font=font)
        draw.text((300, 575), "SIMULATED", fill='#999', anchor='mm', font=small_font)
        
        output_path = self.output_dir / 'f1_passport_photo.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_passport_biopage(self, applicant_data: dict) -> Path:
        """Cria página biográfica do passaporte brasileiro"""
        img = Image.new('RGB', (1200, 800), color='white')
        draw = ImageDraw.Draw(img)
        
        # Fundo
        draw.rectangle([0, 0, 1200, 800], fill='#f8f9fa')
        
        # Header brasileiro (verde e amarelo)
        draw.rectangle([0, 0, 1200, 80], fill='#009b3a')
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            title_font = label_font = data_font = ImageFont.load_default()
        
        draw.text((600, 40), "REPÚBLICA FEDERATIVA DO BRASIL", fill='white', anchor='mm', font=title_font)
        
        # Foto placeholder
        draw.rectangle([50, 120, 320, 490], fill='#e3f2fd', outline='#1565c0', width=3)
        draw.text((185, 305), "PHOTO", fill='#1565c0', anchor='mm', font=title_font)
        
        # Dados
        y_pos = 120
        x_label = 360
        x_data = 600
        line_height = 45
        
        fields = [
            ("Type/Tipo", "P"),
            ("Country Code/País", "BRA"),
            ("Passport No./Passaporte", applicant_data.get('passport_number', 'BR123456789')),
            ("Surname/Sobrenome", applicant_data.get('family_name', 'OLIVEIRA')),
            ("Given Names/Nome", applicant_data.get('given_name', 'RAFAEL SANTOS')),
            ("Nationality/Nacionalidade", "BRAZILIAN"),
            ("Date of Birth/Data Nasc.", applicant_data.get('dob', '15 MAR/MAR 1998')),
            ("Sex/Sexo", applicant_data.get('gender', 'M')),
            ("Place of Birth/Local Nasc.", "São Paulo, BRA"),
            ("Date of Issue/Emissão", applicant_data.get('passport_issue_date', '10 JAN/JAN 2022')),
            ("Date of Expiry/Validade", applicant_data.get('passport_expiry_date', '09 JAN/JAN 2032')),
        ]
        
        for label, value in fields:
            draw.text((x_label, y_pos), label, fill='#555', font=label_font)
            draw.text((x_data, y_pos + 20), value, fill='#000', font=data_font)
            y_pos += line_height
        
        # MRZ (Machine Readable Zone)
        draw.rectangle([0, 720, 1200, 800], fill='#e0e0e0')
        mrz_font = ImageFont.load_default()
        mrz1 = f"P<BRA{applicant_data.get('family_name', 'OLIVEIRA').replace(' ', '<')}<<{applicant_data.get('given_name', 'RAFAEL SANTOS').replace(' ', '<')}"[:44]
        mrz2 = f"{applicant_data.get('passport_number', 'BR123456789')}BRA9803155M3201091<<<<<<<<<<<<<<<0"[:44]
        
        draw.text((50, 735), mrz1, fill='#000', font=mrz_font)
        draw.text((50, 760), mrz2, fill='#000', font=mrz_font)
        
        # Watermark
        draw.text((600, 400), "SIMULATED DOCUMENT", fill='#ddd', anchor='mm', font=title_font)
        
        output_path = self.output_dir / 'f1_passport_biopage.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_i20_form(self, applicant_data: dict, i20_data: dict, program_data: dict) -> Path:
        """Cria simulação visual do Form I-20"""
        img = Image.new('RGB', (2550, 3300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            section_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            title_font = section_font = label_font = data_font = small_font = ImageFont.load_default()
        
        # Header com logo DHS
        draw.rectangle([0, 0, 2550, 220], fill='#1565c0')
        draw.text((1275, 80), "U.S. DEPARTMENT OF HOMELAND SECURITY", fill='white', anchor='mm', font=section_font)
        draw.text((1275, 140), "CERTIFICATE OF ELIGIBILITY FOR NONIMMIGRANT STUDENT STATUS", 
                 fill='white', anchor='mm', font=label_font)
        draw.text((1275, 180), "(F-1 Student)", fill='white', anchor='mm', font=label_font)
        
        # Form number
        draw.rectangle([0, 220, 2550, 310], fill='#e3f2fd')
        draw.text((150, 265), "OMB No. 1653-0038", fill='#1565c0', font=label_font)
        draw.text((2400, 265), "FORM I-20", fill='#1565c0', anchor='rm', font=title_font)
        
        # Instructions
        y_pos = 350
        draw.text((100, y_pos), "PLEASE READ INSTRUCTIONS ON PAGE 2 BEFORE COMPLETING THIS FORM", 
                 fill='#c62828', font=label_font)
        
        # Section 1: School Information
        y_pos = 450
        draw.rectangle([50, y_pos, 2500, y_pos+50], fill='#1565c0')
        draw.text((100, y_pos+25), "1. School Information", fill='white', font=section_font)
        
        y_pos += 80
        school_fields = [
            ("School Name:", program_data.get('school_name', 'Boston University')),
            ("School Address:", program_data.get('school_address', '1 Silber Way, Boston, MA 02215')),
            ("School Code (SEVIS):", program_data.get('sevis_school_code', 'BOS214F00567000')),
            ("", ""),
            ("Designated School Official (DSO):", i20_data.get('dso_name', 'Dr. Jennifer Martinez')),
            ("DSO Title:", i20_data.get('dso_title', 'International Student Advisor')),
            ("DSO Phone:", i20_data.get('dso_phone', '(617) 353-3565')),
        ]
        
        for label, value in school_fields:
            if label:
                draw.text((100, y_pos), label, fill='#1565c0', font=label_font)
                draw.rectangle([100, y_pos+35, 2400, y_pos+80], fill='#f5f5f5', outline='#999', width=2)
                draw.text((120, y_pos+50), value, fill='#000', font=data_font)
                y_pos += 100
            else:
                y_pos += 20
        
        # Section 2: Student Information
        y_pos += 50
        draw.rectangle([50, y_pos, 2500, y_pos+50], fill='#1565c0')
        draw.text((100, y_pos+25), "2. Student Information", fill='white', font=section_font)
        
        y_pos += 80
        student_fields = [
            ("Family Name (Surname):", applicant_data.get('family_name', 'OLIVEIRA')),
            ("First (Given) Name:", applicant_data.get('given_name', 'Rafael Santos')),
            ("Country of Birth:", applicant_data.get('country_of_birth', 'Brazil')),
            ("Date of Birth (mm/dd/yyyy):", applicant_data.get('dob_formatted', '03/15/1998')),
            ("Country of Citizenship:", applicant_data.get('nationality', 'Brazil')),
        ]
        
        for label, value in student_fields:
            draw.text((100, y_pos), label, fill='#1565c0', font=label_font)
            draw.rectangle([100, y_pos+35, 2400, y_pos+80], fill='#f5f5f5', outline='#999', width=2)
            draw.text((120, y_pos+50), value, fill='#000', font=data_font)
            y_pos += 100
        
        # Section 3: Immigration Information
        y_pos += 50
        draw.rectangle([50, y_pos, 2500, y_pos+50], fill='#1565c0')
        draw.text((100, y_pos+25), "3. Immigration Information", fill='white', font=section_font)
        
        y_pos += 80
        immigration_fields = [
            ("SEVIS ID Number:", i20_data.get('sevis_id', 'N0012345678')),
            ("Form I-20 ID Number:", i20_data.get('i20_number', 'N0012345678')),
            ("Admission Number:", "To be assigned at port of entry"),
        ]
        
        for label, value in immigration_fields:
            draw.text((100, y_pos), label, fill='#1565c0', font=label_font)
            draw.rectangle([100, y_pos+35, 2400, y_pos+80], fill='#f5f5f5', outline='#999', width=2)
            draw.text((120, y_pos+50), value, fill='#000', font=data_font)
            y_pos += 100
        
        # Section 4: School & Program Information
        y_pos += 50
        draw.rectangle([50, y_pos, 2500, y_pos+50], fill='#1565c0')
        draw.text((100, y_pos+25), "4. School and Program Information", fill='white', font=section_font)
        
        y_pos += 80
        program_fields = [
            ("Degree/Program:", program_data.get('program_name', 'Master of Science in Computer Science')),
            ("Major/Field of Study:", program_data.get('specialization', 'Machine Learning and AI')),
            ("Level of Education:", program_data.get('program_level', 'Graduate (Master\'s)')),
            ("Program Start Date:", program_data.get('start_date', 'September 3, 2025')),
            ("Program End Date:", program_data.get('expected_completion', 'May 15, 2027')),
        ]
        
        for label, value in program_fields:
            draw.text((100, y_pos), label, fill='#1565c0', font=label_font)
            draw.rectangle([100, y_pos+35, 2400, y_pos+80], fill='#f5f5f5', outline='#999', width=2)
            draw.text((120, y_pos+50), value, fill='#000', font=data_font)
            y_pos += 100
        
        # Section 5: Financial Information (CRITICAL)
        y_pos += 50
        draw.rectangle([50, y_pos, 2500, y_pos+50], fill='#c62828')
        draw.text((100, y_pos+25), "5. School Certification - Financial Information", fill='white', font=section_font)
        
        y_pos += 80
        draw.text((100, y_pos), "Funds available for 12 months:", fill='#c62828', font=label_font)
        y_pos += 50
        
        financial_table = [
            ("Tuition and Fees", i20_data.get('tuition_fees', '$32,000')),
            ("Living Expenses", i20_data.get('living_expenses', '$18,000')),
            ("Books and Supplies", i20_data.get('books_supplies', '$1,500')),
            ("Health Insurance", i20_data.get('health_insurance', '$2,500')),
            ("Personal Expenses", i20_data.get('personal_expenses', '$3,000')),
        ]
        
        for item, amount in financial_table:
            draw.rectangle([100, y_pos, 1800, y_pos+60], fill='white', outline='#999', width=2)
            draw.text((120, y_pos+25), item, fill='#000', font=label_font)
            draw.rectangle([1800, y_pos, 2400, y_pos+60], fill='#fff9c4', outline='#999', width=2)
            draw.text((2380, y_pos+25), amount, fill='#c62828', anchor='rm', font=data_font)
            y_pos += 60
        
        # Total
        draw.rectangle([100, y_pos, 2400, y_pos+80], fill='#c62828')
        draw.text((120, y_pos+35), "TOTAL PER YEAR:", fill='white', font=section_font)
        draw.text((2380, y_pos+35), i20_data.get('total_annual_cost', '$57,000'), 
                 fill='white', anchor='rm', font=title_font)
        
        # Footer
        y_pos = 3150
        draw.rectangle([0, y_pos, 2550, 3300], fill='#f5f5f5')
        draw.text((1275, y_pos+50), "THIS IS A SIMULATED I-20 FOR DOCUMENTATION PURPOSES", 
                 fill='#999', anchor='mm', font=section_font)
        draw.text((1275, y_pos+100), "Official I-20 must be issued by SEVIS-certified school", 
                 fill='#666', anchor='mm', font=label_font)
        
        output_path = self.output_dir / 'f1_i20_form.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_transcript(self, applicant_data: dict, education_data: dict) -> Path:
        """Cria transcrição acadêmica simulada"""
        img = Image.new('RGB', (2550, 3300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
            section_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except:
            title_font = section_font = label_font = data_font = ImageFont.load_default()
        
        # Header USP
        draw.rectangle([0, 0, 2550, 250], fill='#8b0000')
        draw.text((1275, 125), education_data.get('institution', 'UNIVERSIDADE DE SÃO PAULO'), 
                 fill='white', anchor='mm', font=title_font)
        
        # Student info
        y_pos = 300
        draw.text((100, y_pos), "OFFICIAL ACADEMIC TRANSCRIPT", fill='#8b0000', font=section_font)
        y_pos += 80
        
        info = [
            ("Student Name:", applicant_data.get('full_name', 'Rafael Santos Oliveira')),
            ("Student ID:", "USP-2016-12345"),
            ("Program:", education_data.get('field_of_study', 'Computer Science')),
            ("Degree:", education_data.get('highest_degree', 'Bachelor of Science')),
            ("Graduation Date:", education_data.get('graduation_date', 'December 2020')),
        ]
        
        for label, value in info:
            draw.text((100, y_pos), label, fill='#000', font=label_font)
            draw.text((800, y_pos), value, fill='#000', font=data_font)
            y_pos += 50
        
        # Courses table header
        y_pos += 100
        draw.rectangle([100, y_pos, 2400, y_pos+60], fill='#8b0000')
        draw.text((150, y_pos+25), "COURSE", fill='white', font=label_font)
        draw.text((1600, y_pos+25), "CREDITS", fill='white', font=label_font)
        draw.text((2000, y_pos+25), "GRADE", fill='white', font=label_font)
        
        # Sample courses
        courses = [
            ("Data Structures and Algorithms", "4", "A"),
            ("Machine Learning", "4", "A"),
            ("Database Systems", "4", "A-"),
            ("Software Engineering", "4", "B+"),
            ("Artificial Intelligence", "4", "A"),
            ("Computer Networks", "4", "B+"),
            ("Operating Systems", "4", "A-"),
            ("Web Development", "4", "A"),
        ]
        
        y_pos += 60
        for course, credits, grade in courses:
            draw.rectangle([100, y_pos, 2400, y_pos+50], outline='#ccc', width=1)
            draw.text((150, y_pos+20), course, fill='#000', font=data_font)
            draw.text((1650, y_pos+20), credits, fill='#000', font=data_font)
            draw.text((2050, y_pos+20), grade, fill='#000', font=data_font)
            y_pos += 50
        
        # GPA
        y_pos += 50
        draw.rectangle([100, y_pos, 2400, y_pos+80], fill='#f5f5f5')
        draw.text((150, y_pos+35), f"CUMULATIVE GPA: {education_data.get('gpa', '3.7/4.0')}", 
                 fill='#8b0000', font=section_font)
        
        # Footer
        y_pos = 3200
        draw.text((1275, y_pos), "SIMULATED TRANSCRIPT FOR DOCUMENTATION PURPOSES", 
                 fill='#999', anchor='mm', font=label_font)
        
        output_path = self.output_dir / 'f1_transcript.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def create_bank_statement(self, applicant_data: dict, bank_data: dict, month: str) -> Path:
        """Cria extrato bancário brasileiro simulado"""
        img = Image.new('RGB', (2550, 3300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
            section_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            title_font = section_font = label_font = data_font = ImageFont.load_default()
        
        # Header Banco do Brasil
        draw.rectangle([0, 0, 2550, 250], fill='#ffcc00')
        draw.text((1275, 125), "BANCO DO BRASIL", fill='#003399', anchor='mm', font=title_font)
        
        # Account info
        y_pos = 300
        draw.text((100, y_pos), f"Account Statement - {month}", fill='#003399', font=section_font)
        y_pos += 80
        
        draw.text((100, y_pos), f"Account Holder: {applicant_data.get('full_name', 'Rafael Santos Oliveira')}", 
                 fill='#000', font=data_font)
        y_pos += 60
        draw.text((100, y_pos), f"Account Number: {bank_data.get('account_number', '12345-6')}", 
                 fill='#000', font=data_font)
        y_pos += 60
        draw.text((100, y_pos), f"Account Type: {bank_data.get('account_type', 'Savings Account')}", 
                 fill='#000', font=data_font)
        
        # Summary
        y_pos += 120
        draw.rectangle([50, y_pos, 2500, y_pos+250], fill='#f0f0f0', outline='#003399', width=3)
        summary_y = y_pos + 30
        
        draw.text((100, summary_y), "ACCOUNT SUMMARY", fill='#003399', font=section_font)
        summary_y += 70
        
        draw.text((100, summary_y), "Opening Balance:", fill='#000', font=label_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('opening_balance', '225,000.00')}", 
                 fill='#000', font=data_font, anchor='rm')
        summary_y += 50
        
        draw.text((100, summary_y), "Total Credits:", fill='#000', font=label_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('credits', '8,500.00')}", 
                 fill='#006600', font=data_font, anchor='rm')
        summary_y += 50
        
        draw.text((100, summary_y), "Total Debits:", fill='#000', font=label_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('debits', '4,000.00')}", 
                 fill='#cc0000', font=data_font, anchor='rm')
        summary_y += 50
        
        draw.text((100, summary_y), "CLOSING BALANCE:", fill='#003399', font=section_font)
        draw.text((2400, summary_y), f"R$ {bank_data.get('closing_balance', '229,500.00')}", 
                 fill='#003399', font=title_font, anchor='rm')
        
        # Transactions table
        y_pos += 350
        draw.rectangle([50, y_pos, 2500, y_pos+50], fill='#003399')
        draw.text((100, y_pos+15), "Date", fill='white', font=label_font)
        draw.text((500, y_pos+15), "Description", fill='white', font=label_font)
        draw.text((1800, y_pos+15), "Amount", fill='white', font=label_font)
        draw.text((2200, y_pos+15), "Balance", fill='white', font=label_font)
        
        # Sample transactions
        transactions = [
            ("01/03", "SALARY DEPOSIT", "+8,500.00", "225,000.00"),
            ("05/03", "SUPERMARKET", "-850.00", "224,150.00"),
            ("10/03", "RENT PAYMENT", "-2,000.00", "222,150.00"),
            ("15/03", "UTILITIES", "-380.00", "221,770.00"),
            ("20/03", "ATM WITHDRAWAL", "-500.00", "221,270.00"),
            ("25/03", "TRANSFER FROM SAVINGS", "+8,230.00", "229,500.00"),
        ]
        
        y_pos += 50
        for date, desc, amount, balance in transactions:
            color = '#006600' if '+' in amount else '#000'
            draw.text((100, y_pos), date, fill='#000', font=label_font)
            draw.text((500, y_pos), desc, fill='#000', font=label_font)
            draw.text((1900, y_pos), amount, fill=color, font=data_font, anchor='rm')
            draw.text((2300, y_pos), balance, fill='#000', font=data_font, anchor='rm')
            draw.rectangle([50, y_pos + 40, 2500, y_pos + 41], fill='#ddd')
            y_pos += 45
        
        # Footer
        y_pos = 3200
        draw.text((1275, y_pos), "SIMULATED BANK STATEMENT FOR DOCUMENTATION PURPOSES", 
                 fill='#999', anchor='mm', font=label_font)
        
        output_path = self.output_dir / f'f1_bank_statement_{month.replace(" ", "_")}.png'
        img.save(output_path, 'PNG', quality=95)
        return output_path


if __name__ == '__main__':
    """Teste do gerador"""
    from f1_student_data_model import f1_student_case
    
    print("\n🖼️  GERANDO IMAGENS SIMULADAS PARA F-1 PACKAGE")
    print("=" * 60)
    
    generator = F1ImageGenerator()
    
    print("\n1. Gerando foto do passaporte...")
    photo = generator.create_passport_photo(f1_student_case.applicant)
    print(f"   ✅ {photo}")
    
    print("\n2. Gerando página biográfica do passaporte...")
    biopage = generator.create_passport_biopage(f1_student_case.applicant)
    print(f"   ✅ {biopage}")
    
    print("\n3. Gerando Form I-20 visual...")
    i20 = generator.create_i20_form(f1_student_case.applicant, f1_student_case.i20, f1_student_case.us_program)
    print(f"   ✅ {i20}")
    
    print("\n4. Gerando transcrição acadêmica...")
    transcript = generator.create_transcript(f1_student_case.applicant, f1_student_case.education)
    print(f"   ✅ {transcript}")
    
    print("\n5. Gerando extrato bancário...")
    bank_data = {
        'account_number': '12345-6',
        'account_type': 'Savings Account',
        'opening_balance': '225,000.00',
        'credits': '8,500.00',
        'debits': '4,000.00',
        'closing_balance': '229,500.00'
    }
    statement = generator.create_bank_statement(f1_student_case.applicant, bank_data, "March 2025")
    print(f"   ✅ {statement}")
    
    print("\n✅ TODAS AS IMAGENS GERADAS COM SUCESSO!")
    print("=" * 60)
