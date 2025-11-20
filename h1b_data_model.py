"""
H-1B Application Data Model
Todos os dados da aplicação em um único lugar para garantir consistência
"""

from datetime import datetime, timedelta
from typing import Dict, List

class H1BApplicationData:
    """Modelo de dados completo e consistente para uma aplicação H-1B"""
    
    def __init__(self):
        # BENEFICIARY - Todas as informações devem ser consistentes
        self.beneficiary = {
            "full_name": "FERNANDA OLIVEIRA SANTOS",
            "family_name": "SANTOS",
            "given_name": "FERNANDA OLIVEIRA",
            "maiden_name": "OLIVEIRA",
            "dob": "August 15, 1990",
            "dob_formatted": "08/15/1990",
            "age": 34,  # Ela nasceu em Ago 1990, ainda não fez aniversário em 2024
            "pob_city": "São Paulo",
            "pob_state": "São Paulo",
            "pob_country": "Brazil",
            "nationality": "Brazilian",
            "gender": "Female",
            "marital_status": "Single",
            
            # Passport
            "passport_number": "BR789456123",
            "passport_issue_date": "01/15/2019",
            "passport_issue_place": "Departamento de Polícia Federal, São Paulo",
            "passport_expiry_date": "12/31/2028",
            
            # Contact
            "email": "fernanda.santos@gmail.com",
            "phone_brazil": "+55 (11) 98765-4321",
            "phone_us": "+1 (408) 555-0123",
            "address_brazil": "Rua Augusta, 1234, Apartamento 56, São Paulo, SP 01305-100, Brazil",
            
            # Education - MASTER'S DEGREE (consistente em todo documento)
            "masters_institution": "Universidade de São Paulo (USP)",
            "masters_degree": "Master of Science in Computer Science",
            "masters_graduation_date": "December 2015",
            "masters_gpa": "3.85/4.00",
            "masters_gpa_scale": "4.00",
            "masters_honors": "Summa Cum Laude",
            "masters_thesis_title": "Scalable Microservices Architecture for Real-Time Data Processing",
            "masters_advisor": "Dr. Paulo Roberto Silva",
            
            # Education - BACHELOR'S DEGREE
            "bachelors_institution": "Universidade de São Paulo (USP)",
            "bachelors_degree": "Bachelor of Science in Computer Science",
            "bachelors_graduation_date": "December 2013",
            "bachelors_gpa": "3.75/4.00",
            "bachelors_honors": "Magna Cum Laude",
            
            # Professional Experience - TOTAL ÚNICO
            # Jun 2015 - Feb 2018 (2y 9m) + Mar 2018 - Dec 2021 (3y 10m) + Jan 2022 - Oct 2024 (2y 10m) = 9y 5m
            "total_experience_years": 9,
            "total_experience_months": 5,
            
            # Professional Experience - Job 1 (MAIS RECENTE)
            "job1_title": "Technical Lead",
            "job1_company": "Brazilian Startup Accelerator",
            "job1_location": "São Paulo, Brazil",
            "job1_start_date": "January 2022",
            "job1_end_date": "October 2024",
            "job1_duration_years": 2,
            "job1_duration_months": 10,
            "job1_team_size": 8,  # NÚMERO FIXO - ela liderou 8 engenheiros
            "job1_responsibilities": [
                "Led technical architecture for 5 early-stage startups",
                "Designed microservices serving 100,000+ daily active users",
                "Mentored team of 8 engineers (2 senior, 4 mid-level, 2 junior)",
                "Reduced application latency by 60% through optimization",
                "Implemented CI/CD pipelines reducing deployment time by 94%"
            ],
            "job1_key_achievement": "Reduced latency by 60%",
            "job1_budget_managed": "$2,000,000",  # NÚMERO FIXO
            
            # Professional Experience - Job 2
            "job2_title": "Senior Software Developer",
            "job2_company": "Digital Innovations Ltd.",
            "job2_location": "São Paulo, Brazil",
            "job2_start_date": "March 2018",
            "job2_end_date": "December 2021",
            "job2_duration_years": 3,
            "job2_duration_months": 10,
            "job2_team_size": 4,  # Colaborou com 4 pessoas
            "job2_responsibilities": [
                "Developed e-commerce platform processing $10M+ annually",
                "Built APIs handling 1,000,000+ requests per day",
                "Led migration to microservices improving scalability by 300%",
                "Achieved 95%+ code coverage through automated testing"
            ],
            
            # Professional Experience - Job 3 (PRIMEIRO EMPREGO)
            "job3_title": "Software Engineer",
            "job3_company": "Tech Solutions Brazil",
            "job3_location": "São Paulo, Brazil",
            "job3_start_date": "June 2015",
            "job3_end_date": "February 2018",
            "job3_duration_years": 2,
            "job3_duration_months": 9,
            
            # Skills
            "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "Go", "C++", "SQL"],
            "frameworks": ["React", "Node.js", "Django", "Spring Boot", "Flask", "FastAPI"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra"],
            "cloud_platforms": ["Google Cloud Platform", "AWS", "Azure"],
            "tools": ["Docker", "Kubernetes", "Jenkins", "Git", "Terraform"],
        }
        
        # EMPLOYER - Google LLC
        self.employer = {
            "legal_name": "Google LLC",
            "dba": "Google",
            "ein": "77-0493581",
            "incorporation_date": "September 4, 1998",
            "incorporation_state": "Delaware",
            "address": "1600 Amphitheatre Parkway",
            "city": "Mountain View",
            "state": "CA",
            "zip": "94043",
            "phone": "(650) 253-0000",
            "fax": "(650) 253-0001",
            "email": "immigration@google.com",
            "website": "www.google.com",
            
            # Financial (FY 2023) - NÚMEROS CONSISTENTES
            "year_established": 1998,
            "employees_worldwide": "190,234",
            "employees_us": "123,456",
            "employees_california": "89,456",
            "revenue_2023": "$282,836,000,000",
            "revenue_2022": "$257,637,000,000",
            "net_income_2023": "$59,972,000,000",
            "net_income_2022": "$52,498,000,000",
            "total_assets_2023": "$402,392,000,000",
            
            # Immigration Contact
            "immigration_contact_name": "Sarah M. Johnson",
            "immigration_contact_title": "Senior Immigration Specialist",
            "immigration_contact_phone": "(650) 253-0000 ext. 5234",
            "immigration_contact_email": "sjohnson@google.com",
        }
        
        # POSITION
        self.position = {
            "title": "Senior Software Engineer",
            "department": "Cloud Platform Engineering",
            "division": "Technical Infrastructure",
            "soc_code": "15-1252.00",
            "soc_title": "Software Developers, Applications",
            "naics_code": "518210",
            
            # Compensation - NÚMEROS FIXOS
            "salary_annual": "$145,000",
            "salary_annual_numeric": 145000,
            "salary_hourly": "$69.71",
            "bonus_target_percent": "15%",
            "bonus_target_amount": "$21,750",
            "rsu_total": "$50,000",
            "rsu_vesting_period": "4 years",
            "rsu_annual": "$12,500",
            
            # Work Details
            "work_address": "2700 Campus Drive, San Jose, CA 95134",
            "work_building": "Building 3",
            "work_floor": "4th Floor",
            "hours_per_week": 40,
            "schedule": "Monday-Friday, 9:00 AM - 5:00 PM (flexible)",
            
            # Dates
            "start_date": "March 1, 2025",
            "start_date_formatted": "03/01/2025",
            "end_date": "February 28, 2028",
            "end_date_formatted": "02/28/2028",
            "duration_years": 3,
            
            # Reporting
            "reports_to_name": "Michael Chen",
            "reports_to_title": "Director of Engineering",
            "team_lead_name": "Emily Rodriguez",
            "team_lead_title": "Senior Engineering Manager",
        }
        
        # LABOR CONDITION APPLICATION
        self.lca = {
            "certification_number": "I-200-24123-456789",
            "certification_date": "December 15, 2024",
            "certification_date_formatted": "12/15/2024",
            "validity_start": "March 1, 2025",
            "validity_end": "February 28, 2028",
            
            # Wage Information - DEVE BATER COM POSITION
            "wage_offered": "$145,000",
            "wage_offered_numeric": 145000,
            "prevailing_wage": "$138,000",
            "prevailing_wage_numeric": 138000,
            "wage_source": "OES 2024",
            "wage_level": "Level III (Experienced)",
            
            "certifying_officer": "Robert J. Martinez",
            "certifying_officer_title": "Certifying Officer, OFLC",
        }
        
        # CASE INFORMATION
        self.case_info = {
            "case_number": f"H1B-GOOGLE-{datetime.now().strftime('%Y%m%d')}-001",
            "petition_date": datetime.now().strftime("%B %d, %Y"),
            "petition_date_formatted": datetime.now().strftime("%m/%d/%Y"),
            "prepared_by": "Sarah M. Johnson",
            "prepared_by_title": "Senior Immigration Specialist",
        }
    
    def validate_consistency(self) -> List[str]:
        """Valida consistência dos dados"""
        errors = []
        
        # 1. Verificar que salário oferecido >= prevailing wage
        if self.position['salary_annual_numeric'] < self.lca['prevailing_wage_numeric']:
            errors.append(f"ERRO: Salário oferecido (${self.position['salary_annual_numeric']}) é menor que prevailing wage (${self.lca['prevailing_wage_numeric']})")
        
        # 2. Verificar que datas do LCA batem com datas de emprego
        if self.lca['validity_start'] != self.position['start_date']:
            errors.append(f"ERRO: Data início LCA ({self.lca['validity_start']}) diferente de data início emprego ({self.position['start_date']})")
        
        if self.lca['validity_end'] != self.position['end_date']:
            errors.append(f"ERRO: Data fim LCA ({self.lca['validity_end']}) diferente de data fim emprego ({self.position['end_date']})")
        
        # 3. Verificar experiência total
        expected_exp = (self.beneficiary['job1_duration_years'] + 
                       self.beneficiary['job2_duration_years'] + 
                       self.beneficiary['job3_duration_years'])
        if self.beneficiary['total_experience_years'] != expected_exp:
            errors.append(f"AVISO: Experiência total ({self.beneficiary['total_experience_years']} anos) não bate com soma dos empregos ({expected_exp} anos)")
        
        # 4. Verificar idade vs data de nascimento (nasceu em Agosto 1990)
        birth_year = 1990
        current_year = datetime.now().year
        current_month = datetime.now().month
        # Se ainda não fez aniversário este ano (antes de agosto), idade é current_year - birth_year - 1
        if current_month < 8:
            expected_age = current_year - birth_year - 1
        else:
            expected_age = current_year - birth_year
        if self.beneficiary['age'] != expected_age:
            errors.append(f"ERRO: Idade ({self.beneficiary['age']}) não bate com data de nascimento (deveria ser {expected_age})")
        
        return errors
    
    def get_summary(self) -> Dict:
        """Retorna resumo dos dados"""
        return {
            "beneficiary_name": self.beneficiary['full_name'],
            "position": self.position['title'],
            "employer": self.employer['legal_name'],
            "salary": self.position['salary_annual'],
            "start_date": self.position['start_date'],
            "total_experience": f"{self.beneficiary['total_experience_years']} years",
            "education": self.beneficiary['masters_degree'],
            "lca_certified": self.lca['certification_date'],
        }

# Criar instância global
h1b_data = H1BApplicationData()

# Validar na importação
validation_errors = h1b_data.validate_consistency()
if validation_errors:
    print("⚠️ AVISOS DE VALIDAÇÃO:")
    for error in validation_errors:
        print(f"  - {error}")
else:
    print("✅ Dados validados com sucesso - sem inconsistências")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("H-1B APPLICATION DATA MODEL")
    print("="*80)
    print("\nResumo da Aplicação:")
    summary = h1b_data.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("VALIDAÇÃO DE CONSISTÊNCIA")
    print("="*80)
    errors = h1b_data.validate_consistency()
    if errors:
        print("❌ Erros encontrados:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Todos os dados estão consistentes!")
