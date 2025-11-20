#!/usr/bin/env python3
"""
Dados de Caso Simulado - Aplicação H-1B Completa
Caso hipotético para demonstração do sistema
"""

from datetime import datetime
from typing import Dict, List


class SimulatedH1BCase:
    """Modelo de dados para caso simulado de H-1B"""
    
    def __init__(self):
        # Informações do Beneficiário
        self.beneficiary = {
            "full_name": "RICARDO ANTONIO SILVA MENDES",
            "family_name": "SILVA MENDES",
            "given_name": "RICARDO ANTONIO",
            "maiden_name": "N/A",
            "dob": "March 22, 1988",
            "dob_formatted": "03/22/1988",
            "age": 37,
            "pob_city": "Rio de Janeiro",
            "pob_state": "Rio de Janeiro",
            "pob_country": "Brazil",
            "nationality": "Brazilian",
            "gender": "Male",
            "marital_status": "Married",
            
            # Passport
            "passport_number": "BR456789321",
            "passport_issue_date": "05/10/2020",
            "passport_issue_place": "Departamento de Polícia Federal, Rio de Janeiro",
            "passport_expiry_date": "05/09/2030",
            
            # Educação
            "bachelors_degree": "Bachelor of Science in Computer Engineering",
            "bachelors_institution": "Universidade Federal do Rio de Janeiro (UFRJ)",
            "bachelors_graduation_year": "2010",
            "bachelors_gpa": "3.8/4.0",
            "bachelors_honors": "Cum Laude",
            
            "masters_degree": "Master of Science in Artificial Intelligence",
            "masters_institution": "Stanford University",
            "masters_graduation_year": "2013",
            "masters_graduation_date": "June 15, 2013",
            "masters_gpa": "3.9/4.0",
            "masters_honors": "With Distinction",
            
            # Experiência
            "total_experience_years": 12,
            "current_employer": "Amazon Web Services",
            "current_position": "Senior Machine Learning Engineer",
            "current_employment_start": "2018",
            
            # Contato
            "email": "ricardo.silva@email.com",
            "phone": "+1 (650) 555-0199",
            "current_address": "2450 Garcia Avenue, Apt 302",
            "current_city": "Mountain View",
            "current_state": "CA",
            "current_zip": "94043",
            
            # Entrada nos EUA
            "last_entry_date": "08/15/2018",
            "last_entry_port": "San Francisco International Airport",
            "current_status": "L-1B",
            "status_expiry": "08/14/2026",
            "i94_number": "94567891234",
        }
        
        # Informações do Empregador (Peticionário)
        self.employer = {
            "legal_name": "Microsoft Corporation",
            "dba_name": "Microsoft",
            "fein": "91-1144442",
            "address": "One Microsoft Way",
            "city": "Redmond",
            "state": "WA",
            "zip": "98052",
            "phone": "+1 (425) 882-8080",
            "email": "immigration@microsoft.com",
            "website": "www.microsoft.com",
            
            # Detalhes da empresa
            "year_established": "1975",
            "business_type": "Technology - Software and Cloud Services",
            "naics_code": "511210",
            "employee_count": "221,000",
            "revenue_2023": "$211.9 billion",
            "revenue_2022": "$198.3 billion",
            
            # Contato
            "hr_contact_name": "Sarah Mitchell",
            "hr_contact_title": "Director of Global Immigration",
            "hr_contact_email": "s.mitchell@microsoft.com",
            "hr_contact_phone": "+1 (425) 882-8080 ext. 5501",
        }
        
        # Informações da Posição
        self.position = {
            "title": "Principal AI Research Scientist",
            "department": "Microsoft Research - AI Division",
            "soc_code": "15-1221.00",
            "soc_title": "Computer and Information Research Scientists",
            "prevailing_wage_level": "Level IV",
            
            # Salário
            "salary_annual": "$245,000",
            "salary_hourly": "$117.79",
            "hours_per_week": "40",
            
            # Localização
            "work_location_address": "One Microsoft Way",
            "work_location_city": "Redmond",
            "work_location_state": "WA",
            "work_location_zip": "98052",
            
            # Período
            "start_date": "10/01/2025",
            "end_date": "09/30/2028",
            "duration_years": "3",
            
            # Descrição
            "summary": "Lead advanced AI research initiatives, develop cutting-edge machine learning algorithms, and architect scalable AI systems for Microsoft's cloud infrastructure.",
        }
        
        # Informações da LCA (Labor Condition Application)
        self.lca = {
            "certification_number": "I-200-25098-456789",
            "certification_date": "08/15/2025",
            "case_number": "L-250-25098-456789",
            "filing_date": "07/20/2025",
            "decision_date": "08/15/2025",
            "wage_rate": "$245,000 per year",
            "prevailing_wage": "$195,000 per year",
            "validity_start": "10/01/2025",
            "validity_end": "09/30/2028",
        }
        
        # Informações do Caso
        self.case_info = {
            "petition_date": "September 1, 2025",
            "petition_type": "H-1B Initial",
            "service_center": "California Service Center",
            "attorney_name": "Dr. Jennifer Martinez",
            "attorney_bar": "CA Bar #345678",
            "law_firm": "Global Immigration Partners LLP",
            "law_firm_address": "555 Market Street, Suite 2000, San Francisco, CA 94105",
            "case_id": "MS-H1B-2025-0915",
        }


# Instanciar caso simulado
simulated_case = SimulatedH1BCase()
