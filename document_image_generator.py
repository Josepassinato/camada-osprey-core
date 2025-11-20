"""
Gerador de Imagens Fictícias de Documentos
Cria imagens realistas de passaportes, diplomas, certificados, etc.
"""

from PIL import Image, ImageDraw, ImageFont
import os

class DocumentImageGenerator:
    """Gera imagens fictícias de documentos para incluir no pacote"""
    
    def __init__(self, output_dir="/tmp/doc_images"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Tentar carregar fontes do sistema
        try:
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def generate_passport_page(self, full_name, dob, passport_num, issue_date, expiry_date, nationality="Brazilian"):
        """Gera imagem de página biográfica de passaporte"""
        
        # Criar imagem (tamanho padrão de passaporte digitalizado)
        img = Image.new('RGB', (800, 600), color='#d4af37')  # Dourado
        draw = ImageDraw.Draw(img)
        
        # Cabeçalho
        draw.rectangle([0, 0, 800, 80], fill='#8B4513')
        draw.text((30, 20), "REPÚBLICA FEDERATIVA DO BRASIL", fill='white', font=self.font_large)
        draw.text((30, 50), "PASSPORT / PASSAPORTE", fill='white', font=self.font_medium)
        
        # Brasão simulado
        draw.ellipse([700, 10, 780, 70], fill='#FFD700', outline='white', width=3)
        
        # Informações do passaporte
        y_pos = 120
        spacing = 40
        
        fields = [
            ("Type/Tipo:", "P"),
            ("Code of issuing State/Código do país emissor:", "BRA"),
            ("Passport No./Passaporte Nº:", passport_num),
            ("Surname/Sobrenome:", full_name.split()[-1].upper()),
            ("Given names/Prenomes:", " ".join(full_name.split()[:-1]).upper()),
            ("Nationality/Nacionalidade:", nationality),
            ("Date of birth/Data de nascimento:", dob),
            ("Sex/Sexo:", "F"),
            ("Place of birth/Local de nascimento:", "SÃO PAULO, BRAZIL"),
            ("Date of issue/Data de emissão:", issue_date),
            ("Date of expiry/Data de expiração:", expiry_date),
            ("Authority/Autoridade:", "POLÍCIA FEDERAL"),
        ]
        
        for label, value in fields:
            draw.text((30, y_pos), label, fill='#8B4513', font=self.font_small)
            draw.text((30, y_pos + 18), value, fill='black', font=self.font_medium)
            y_pos += spacing
        
        # Foto placeholder
        draw.rectangle([600, 120, 750, 320], fill='#CCCCCC', outline='black', width=2)
        draw.text((625, 200), "PHOTO", fill='#666666', font=self.font_medium)
        
        # MRZ (Machine Readable Zone) no final
        draw.rectangle([0, 550, 800, 600], fill='#333333')
        draw.text((20, 560), "P<BRASOLIVEIRA<<SANTOS<<FERNANDA<<<<<<<<<<<<<", fill='white', font=self.font_small)
        draw.text((20, 575), f"{passport_num}7BRA9008156F2912314<<<<<<<<<<<<<<<06", fill='white', font=self.font_small)
        
        # Salvar
        path = os.path.join(self.output_dir, "passport_bio_page.png")
        img.save(path)
        print(f"✅ Passaporte gerado: {path}")
        return path
    
    def generate_diploma(self, full_name, degree, institution, graduation_date):
        """Gera imagem de diploma universitário"""
        
        img = Image.new('RGB', (1000, 700), color='#FFF8DC')
        draw = ImageDraw.Draw(img)
        
        # Borda decorativa
        draw.rectangle([20, 20, 980, 680], outline='#8B4513', width=5)
        draw.rectangle([30, 30, 970, 670], outline='#DAA520', width=2)
        
        # Cabeçalho
        draw.text((500, 80), institution.upper(), fill='#8B4513', font=self.font_large, anchor="mm")
        draw.text((500, 120), "UNIVERSIDADE DE SÃO PAULO", fill='#8B4513', font=self.font_medium, anchor="mm")
        
        # Corpo do diploma
        draw.text((500, 200), "DIPLOMA", fill='#DAA520', font=self.font_large, anchor="mm")
        draw.text((500, 250), f"Este diploma certifica que", fill='black', font=self.font_medium, anchor="mm")
        draw.text((500, 300), full_name.upper(), fill='#8B4513', font=self.font_large, anchor="mm")
        
        # Descrição do grau
        text_lines = [
            f"concluiu com êxito todos os requisitos para o grau de",
            degree,
            f"conferido em {graduation_date}",
            "",
            "com todas as honras, direitos e privilégios pertinentes."
        ]
        
        y_pos = 360
        for line in text_lines:
            if "Master" in line or "Bachelor" in line:
                draw.text((500, y_pos), line, fill='#8B4513', font=self.font_large, anchor="mm")
            else:
                draw.text((500, y_pos), line, fill='black', font=self.font_medium, anchor="mm")
            y_pos += 40
        
        # Assinaturas
        draw.line([200, 600, 400, 600], fill='black', width=2)
        draw.text((300, 610), "Reitor", fill='black', font=self.font_small, anchor="mm")
        
        draw.line([600, 600, 800, 600], fill='black', width=2)
        draw.text((700, 610), "Secretário", fill='black', font=self.font_small, anchor="mm")
        
        # Selo universitário simulado
        draw.ellipse([450, 500, 550, 600], fill='#FFD700', outline='#8B4513', width=3)
        draw.text((500, 550), "USP", fill='#8B4513', font=self.font_large, anchor="mm")
        
        path = os.path.join(self.output_dir, "diploma.png")
        img.save(path)
        print(f"✅ Diploma gerado: {path}")
        return path
    
    def generate_transcript(self, full_name, institution):
        """Gera imagem de histórico escolar"""
        
        img = Image.new('RGB', (850, 1100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Cabeçalho
        draw.rectangle([0, 0, 850, 120], fill='#003366')
        draw.text((425, 30), institution, fill='white', font=self.font_large, anchor="mm")
        draw.text((425, 70), "OFFICIAL TRANSCRIPT", fill='white', font=self.font_medium, anchor="mm")
        draw.text((425, 95), "HISTÓRICO ESCOLAR OFICIAL", fill='white', font=self.font_small, anchor="mm")
        
        # Informações do estudante
        y_pos = 150
        student_info = [
            f"Student Name / Nome: {full_name.upper()}",
            f"Student ID / Matrícula: USP-2013-045678",
            f"Program / Curso: Computer Science / Ciência da Computação",
            f"Degree / Grau: Master of Science",
        ]
        
        for info in student_info:
            draw.text((50, y_pos), info, fill='black', font=self.font_medium)
            y_pos += 30
        
        # Tabela de disciplinas
        y_pos = 300
        draw.rectangle([50, y_pos, 800, y_pos + 30], fill='#003366')
        draw.text((70, y_pos + 10), "Course / Disciplina", fill='white', font=self.font_small)
        draw.text((500, y_pos + 10), "Credits", fill='white', font=self.font_small)
        draw.text((600, y_pos + 10), "Grade", fill='white', font=self.font_small)
        draw.text((700, y_pos + 10), "Points", fill='white', font=self.font_small)
        
        # Cursos
        courses = [
            ("Advanced Algorithms", "4", "A", "4.00"),
            ("Distributed Systems", "4", "A", "4.00"),
            ("Machine Learning", "4", "A-", "3.67"),
            ("Software Engineering", "3", "A", "4.00"),
            ("Database Systems", "3", "A", "4.00"),
            ("Computer Networks", "3", "B+", "3.33"),
            ("Research Methods", "2", "A", "4.00"),
            ("Master's Thesis", "6", "A", "4.00"),
        ]
        
        y_pos += 40
        for course, credits, grade, points in courses:
            draw.text((70, y_pos), course, fill='black', font=self.font_small)
            draw.text((500, y_pos), credits, fill='black', font=self.font_small)
            draw.text((600, y_pos), grade, fill='black', font=self.font_small)
            draw.text((700, y_pos), points, fill='black', font=self.font_small)
            draw.line([50, y_pos + 20, 800, y_pos + 20], fill='#CCCCCC', width=1)
            y_pos += 30
        
        # GPA
        y_pos += 30
        draw.rectangle([50, y_pos, 800, y_pos + 40], fill='#F0F0F0')
        draw.text((70, y_pos + 15), "Cumulative GPA / Média Geral: 3.85 / 4.00", fill='#003366', font=self.font_medium)
        
        # Rodapé
        draw.text((425, 1050), "Official Document - Documento Oficial", fill='#666666', font=self.font_small, anchor="mm")
        
        path = os.path.join(self.output_dir, "transcript.png")
        img.save(path)
        print(f"✅ Histórico escolar gerado: {path}")
        return path
    
    def generate_recommendation_letter(self, recommender_name, recommender_title):
        """Gera imagem de carta de recomendação"""
        
        img = Image.new('RGB', (850, 1100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Papel timbrado
        draw.rectangle([0, 0, 850, 100], fill='#1a237e')
        draw.text((425, 30), "BRAZILIAN STARTUP ACCELERATOR", fill='white', font=self.font_large, anchor="mm")
        draw.text((425, 65), "Av. Paulista, 1000 - São Paulo, SP - Brazil", fill='white', font=self.font_small, anchor="mm")
        
        # Data e destinatário
        y_pos = 140
        draw.text((50, y_pos), "October 15, 2024", fill='black', font=self.font_medium)
        y_pos += 60
        draw.text((50, y_pos), "U.S. Citizenship and Immigration Services", fill='black', font=self.font_medium)
        y_pos += 25
        draw.text((50, y_pos), "California Service Center", fill='black', font=self.font_medium)
        
        # Assunto
        y_pos += 60
        draw.text((50, y_pos), "RE: Letter of Recommendation for Fernanda Oliveira Santos", fill='#1a237e', font=self.font_medium)
        
        # Corpo da carta
        y_pos += 50
        letter_lines = [
            "Dear Immigration Officer,",
            "",
            "I am writing to strongly recommend Ms. Fernanda Oliveira Santos for H-1B",
            "classification. As her direct supervisor for the past 3 years at Brazilian Startup",
            "Accelerator, I have had the privilege of witnessing her exceptional technical skills",
            "and leadership capabilities firsthand.",
            "",
            "Ms. Santos served as Technical Lead, managing a team of 8 engineers and",
            "overseeing technical infrastructure with a budget of $500,000. Her contributions",
            "include:",
            "",
            "• Led architecture redesign that reduced system latency by 60%",
            "• Managed cross-functional teams across 5 portfolio companies",
            "• Implemented DevOps practices reducing deployment time by 94%",
            "",
            "Her technical expertise, combined with her leadership and communication skills,",
            "make her an invaluable asset. I have no doubt she will excel in her role at Google.",
            "",
            "Please feel free to contact me if you need any additional information.",
            "",
            "Sincerely,",
        ]
        
        for line in letter_lines:
            draw.text((50, y_pos), line, fill='black', font=self.font_small)
            y_pos += 25
        
        # Assinatura
        y_pos += 30
        draw.text((50, y_pos), recommender_name, fill='#1a237e', font=self.font_medium)
        y_pos += 25
        draw.text((50, y_pos), recommender_title, fill='black', font=self.font_small)
        y_pos += 20
        draw.text((50, y_pos), "Brazilian Startup Accelerator", fill='black', font=self.font_small)
        
        path = os.path.join(self.output_dir, "recommendation_letter.png")
        img.save(path)
        print(f"✅ Carta de recomendação gerada: {path}")
        return path
    
    def generate_lca_certified(self, employer_name, position, wage, lca_number, cert_date):
        """Gera imagem de LCA certificado pelo DOL"""
        
        img = Image.new('RGB', (850, 1100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Cabeçalho oficial do DOL
        draw.rectangle([0, 0, 850, 150], fill='#003d7a')
        draw.text((425, 40), "U.S. DEPARTMENT OF LABOR", fill='white', font=self.font_large, anchor="mm")
        draw.text((425, 80), "Employment and Training Administration", fill='white', font=self.font_medium, anchor="mm")
        draw.text((425, 110), "LABOR CONDITION APPLICATION", fill='#FFD700', font=self.font_medium, anchor="mm")
        draw.text((425, 135), "FOR NONIMMIGRANT WORKERS", fill='white', font=self.font_small, anchor="mm")
        
        # Selo CERTIFIED
        draw.ellipse([650, 180, 800, 330], fill='#10b981', outline='white', width=4)
        draw.text((725, 240), "CERTIFIED", fill='white', font=self.font_large, anchor="mm")
        draw.text((725, 280), cert_date, fill='white', font=self.font_small, anchor="mm")
        
        # Informações do LCA
        y_pos = 200
        fields = [
            ("CERTIFICATION NUMBER:", lca_number),
            ("STATUS:", "CERTIFIED"),
            ("", ""),
            ("EMPLOYER INFORMATION:", ""),
            ("Legal Business Name:", employer_name),
            ("", ""),
            ("POSITION INFORMATION:", ""),
            ("Job Title:", position),
            ("SOC Code:", "15-1252.00"),
            ("SOC Title:", "Software Developers"),
            ("", ""),
            ("WAGE INFORMATION:", ""),
            ("Wage Offered:", wage),
            ("Wage Level:", "Level III"),
            ("Prevailing Wage Source:", "OES - Online Wage Library"),
            ("", ""),
            ("WORK LOCATION:", ""),
            ("Address:", "2700 Campus Drive, San Jose, CA 95134"),
        ]
        
        for label, value in fields:
            if "INFORMATION:" in label or "CERTIFIED" in value:
                draw.text((50, y_pos), label, fill='#003d7a', font=self.font_medium)
                if value:
                    draw.text((50, y_pos + 25), value, fill='#10b981' if "CERTIFIED" in value else '#003d7a', font=self.font_medium)
                    y_pos += 50
                else:
                    y_pos += 35
            else:
                if label:
                    draw.text((50, y_pos), f"{label} {value}", fill='black', font=self.font_small)
                y_pos += 25
        
        # Rodapé oficial
        draw.rectangle([0, 1050, 850, 1100], fill='#003d7a')
        draw.text((425, 1075), "Official U.S. Government Document", fill='white', font=self.font_small, anchor="mm")
        
        path = os.path.join(self.output_dir, "lca_certified.png")
        img.save(path)
        print(f"✅ LCA certificado gerado: {path}")
        return path
    
    def generate_i129_form(self):
        """Gera imagem de formulário I-129 preenchido"""
        
        img = Image.new('RGB', (850, 1100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Cabeçalho USCIS
        draw.rectangle([0, 0, 850, 100], fill='#1a237e')
        draw.text((50, 25), "USCIS", fill='white', font=self.font_large)
        draw.text((50, 60), "Form I-129", fill='white', font=self.font_medium)
        draw.text((700, 40), "OMB No. 1615-0009", fill='white', font=self.font_small)
        draw.text((700, 65), "Expires 12/31/2026", fill='white', font=self.font_small)
        
        # Título
        y_pos = 130
        draw.text((50, y_pos), "Petition for a Nonimmigrant Worker", fill='#1a237e', font=self.font_large)
        
        # Seções do formulário
        y_pos = 200
        sections = [
            "Part 1. Information About the Employer",
            "Part 2. Information About This Petition",
            "Part 3. Information About the Person or Organization Filing",
            "Part 4. Information About the Beneficiary",
        ]
        
        for section in sections:
            draw.rectangle([50, y_pos, 800, y_pos + 35], fill='#E8E8E8', outline='#1a237e', width=2)
            draw.text((60, y_pos + 10), section, fill='#1a237e', font=self.font_medium)
            y_pos += 50
            
            # Campos de exemplo
            for i in range(3):
                draw.rectangle([70, y_pos, 780, y_pos + 25], outline='#CCCCCC', width=1)
                draw.text((80, y_pos + 5), f"Field {i+1}: [COMPLETED]", fill='black', font=self.font_small)
                y_pos += 30
            y_pos += 20
        
        # Rodapé
        draw.text((425, 1050), "Form I-129 (Rev. 09/17/21)", fill='#666666', font=self.font_small, anchor="mm")
        draw.text((425, 1075), "Page 1 of 24", fill='#666666', font=self.font_small, anchor="mm")
        
        path = os.path.join(self.output_dir, "form_i129.png")
        img.save(path)
        print(f"✅ Formulário I-129 gerado: {path}")
        return path
    
    def generate_all_documents(self, h1b_data):
        """Gera todos os documentos necessários"""
        
        print("\n" + "="*80)
        print("🎨 GERANDO IMAGENS DE DOCUMENTOS FICTÍCIOS")
        print("="*80)
        
        documents = {}
        
        # Passaporte
        documents['passport'] = self.generate_passport_page(
            h1b_data.beneficiary['full_name'],
            h1b_data.beneficiary['dob'],
            h1b_data.beneficiary['passport_number'],
            h1b_data.beneficiary['passport_issue_date'],
            h1b_data.beneficiary['passport_expiry_date']
        )
        
        # Diploma
        documents['diploma'] = self.generate_diploma(
            h1b_data.beneficiary['full_name'],
            h1b_data.beneficiary['masters_degree'],
            h1b_data.beneficiary['masters_institution'],
            h1b_data.beneficiary['masters_graduation_date']
        )
        
        # Histórico escolar
        documents['transcript'] = self.generate_transcript(
            h1b_data.beneficiary['full_name'],
            h1b_data.beneficiary['masters_institution']
        )
        
        # Carta de recomendação
        documents['recommendation'] = self.generate_recommendation_letter(
            "Dr. Paulo Roberto Silva",
            "Chief Technology Officer"
        )
        
        # LCA certificado
        documents['lca'] = self.generate_lca_certified(
            h1b_data.employer['legal_name'],
            h1b_data.position['title'],
            h1b_data.position['salary_annual'],
            h1b_data.lca['certification_number'],
            h1b_data.lca['certification_date']
        )
        
        # Formulário I-129
        documents['i129'] = self.generate_i129_form()
        
        print(f"\n✅ Total de documentos gerados: {len(documents)}")
        print("="*80)
        
        return documents


if __name__ == "__main__":
    # Teste
    import sys
    sys.path.insert(0, '/app')
    from h1b_data_model import h1b_data
    
    generator = DocumentImageGenerator()
    docs = generator.generate_all_documents(h1b_data)
    
    print("\n📁 Documentos salvos em:", generator.output_dir)
    for doc_type, path in docs.items():
        print(f"   • {doc_type}: {path}")
