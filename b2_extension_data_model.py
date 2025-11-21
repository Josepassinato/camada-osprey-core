#!/usr/bin/env python3
"""
Modelo de Dados para Extensão de Visto B-2 (Tourist Visa Extension)
Form I-539: Application to Extend/Change Nonimmigrant Status
"""

from datetime import datetime, timedelta
from typing import Dict, List


class B2ExtensionCase:
    """Modelo de dados para caso de extensão B-2"""
    
    def __init__(self):
        # Informações do Aplicante (Visitor)
        self.applicant = {
            "full_name": "MARIA HELENA RODRIGUES COSTA",
            "family_name": "RODRIGUES COSTA",
            "given_name": "MARIA HELENA",
            "other_names": "N/A",
            "dob": "April 15, 1965",
            "dob_formatted": "04/15/1965",
            "age": 59,
            "pob_city": "Belo Horizonte",
            "pob_state": "Minas Gerais",
            "pob_country": "Brazil",
            "nationality": "Brazilian",
            "gender": "Female",
            "marital_status": "Married",
            
            # Informações de passaporte
            "passport_number": "BR789456123",
            "passport_issue_date": "03/10/2019",
            "passport_expiry_date": "03/09/2029",
            "passport_country": "Brazil",
            
            # Endereço no Brasil
            "home_address": "Rua das Flores, 245, Apto 801",
            "home_city": "Belo Horizonte",
            "home_state": "Minas Gerais",
            "home_zip": "30130-100",
            "home_country": "Brazil",
            "home_phone": "+55 31 3333-4444",
            
            # Endereço nos EUA
            "us_address": "1234 Palm Avenue, Apt 15B",
            "us_city": "Miami",
            "us_state": "FL",
            "us_zip": "33139",
            "us_phone": "+1 (305) 555-0123",
            
            # Contato
            "email": "maria.costa@email.com.br",
            
            # Ocupação
            "occupation": "Retired Teacher",
            "employer_brazil": "N/A (Retired since 2020)",
        }
        
        # Informações de Imigração Atual
        self.current_status = {
            "visa_type": "B-2 (Tourist)",
            "visa_number": "B2-98765432",
            "visa_issue_date": "11/05/2023",
            "visa_issue_location": "U.S. Embassy, Brasília, Brazil",
            "visa_expiry_date": "11/04/2033",  # Visa de 10 anos
            
            # Entrada nos EUA
            "arrival_date": "12/15/2024",
            "arrival_port": "Miami International Airport (MIA)",
            "arrival_airline": "American Airlines Flight AA 904",
            
            # I-94 Information
            "i94_number": "94123456789012",
            "i94_admit_until_date": "06/13/2025",  # 6 meses
            "current_status_expires": "06/13/2025",
            
            # Status atual
            "days_in_us": 158,  # ~5 meses
            "authorized_stay_days": 180,  # 6 meses padrão
            "overstay_status": "No - Still within authorized period",
        }
        
        # Extensão Solicitada
        self.extension_request = {
            "requested_extension_until": "12/13/2025",  # Mais 6 meses
            "total_requested_days": 180,  # 6 meses adicionais
            "filing_date": "May 20, 2025",
            "days_before_expiration": 24,  # Aplicando 24 dias antes de expirar
            "application_timely": "Yes - Filed before current status expires",
            
            # Razões da extensão
            "primary_reason": "Medical Treatment and Recovery",
            "secondary_reason": "Family Support During Health Crisis",
            
            # Detalhes
            "reason_details": """
            The applicant requires an extension of her B-2 tourist status due to unexpected medical circumstances 
            that arose during her visit to the United States. She was diagnosed with a serious cardiac condition 
            requiring immediate medical intervention and ongoing treatment.
            
            On March 10, 2025, the applicant experienced severe chest pain and was admitted to Mount Sinai Medical 
            Center in Miami Beach, FL, where she was diagnosed with coronary artery disease requiring urgent cardiac 
            catheterization and stent placement. The procedure was successfully performed on March 12, 2025.
            
            Her cardiologist, Dr. Robert Martinez, MD, has recommended a minimum of 6 months of post-procedure 
            monitoring, cardiac rehabilitation, and medication adjustment before she is medically cleared to 
            undertake international air travel. Medical documentation is included with this application.
            
            Additionally, her daughter, a U.S. citizen residing in Miami, is providing essential family support 
            during this recovery period.
            """,
        }
        
        # Informações Financeiras
        self.financial_support = {
            "source": "Personal savings and family support",
            "bank_name": "Banco do Brasil",
            "account_balance": "R$ 485,000 (~$97,000 USD)",
            "monthly_pension": "R$ 8,500 (~$1,700 USD)",
            
            "us_support": {
                "supporter_name": "Ana Paula Costa",
                "supporter_relation": "Daughter",
                "supporter_status": "U.S. Citizen",
                "supporter_occupation": "Registered Nurse",
                "supporter_annual_income": "$78,000",
                "supporter_address": "1234 Palm Avenue, Apt 15B, Miami, FL 33139",
            },
            
            "health_insurance": "Yes - International travel health insurance through Assist Card",
            "insurance_policy": "AC-BR-2024-789456",
            "insurance_coverage": "$150,000 USD",
            "insurance_valid_until": "12/31/2025",
        }
        
        # Família nos EUA
        self.family_in_us = {
            "daughter": {
                "name": "Ana Paula Costa",
                "relation": "Daughter",
                "status": "U.S. Citizen",
                "naturalization_date": "September 15, 2019",
                "certificate_number": "123456789",
                "address": "1234 Palm Avenue, Apt 15B, Miami, FL 33139",
                "phone": "+1 (305) 555-0123",
                "occupation": "Registered Nurse",
                "employer": "Jackson Memorial Hospital",
            },
            
            "grandchildren": [
                {
                    "name": "Gabriel Costa Silva",
                    "age": 12,
                    "status": "U.S. Citizen by birth",
                },
                {
                    "name": "Sofia Costa Silva",
                    "age": 8,
                    "status": "U.S. Citizen by birth",
                }
            ]
        }
        
        # Vínculos com o Brasil (ties to home country)
        self.home_country_ties = {
            # Simplified access fields
            "spouse_name": "João Carlos Rodrigues Costa",
            "spouse_age": 62,
            "spouse_occupation": "Retired Engineer",
            "children_count": 2,
            "children_names": ["Ana Paula Costa", "Lucas Rodrigues Costa"],
            "property_value": "$240,000 USD",
            "years_married": "35 years",
            "years_in_home": "30+ years",
            
            "property": {
                "owns_home": True,
                "property_address": "Rua das Flores, 245, Apto 801, Belo Horizonte, MG",
                "property_value": "R$ 1,200,000 (~$240,000 USD)",
                "property_type": "Owned apartment (paid in full)",
            },
            
            "spouse": {
                "name": "João Carlos Rodrigues Costa",
                "relation": "Husband",
                "location": "Belo Horizonte, Brazil",
                "occupation": "Retired Engineer",
                "note": "Husband remained in Brazil to maintain household and property",
            },
            
            "other_children": {
                "son": {
                    "name": "Lucas Rodrigues Costa",
                    "age": 34,
                    "location": "São Paulo, Brazil",
                    "occupation": "Civil Engineer",
                }
            },
            
            "intent_to_return": "Strong - Applicant has significant family ties, property ownership, "
                               "and established life in Brazil. Extension is solely for medical recovery, "
                               "with definite intent to return home once cleared for travel.",
        }
        
        # Informações Médicas
        self.medical_information = {
            "diagnosis": "Coronary Artery Disease (CAD)",
            "procedure": "Percutaneous Coronary Intervention (PCI) with stent placement",
            "procedure_date": "March 12, 2025",
            "hospital": "Mount Sinai Medical Center, Miami Beach, FL",
            "treating_physician": {
                "name": "Dr. Robert Martinez, MD, FACC",
                "specialty": "Interventional Cardiology",
                "address": "4300 Alton Road, Miami Beach, FL 33140",
                "phone": "+1 (305) 674-2121",
                "medical_license": "FL ME 123456",
            },
            "recovery_period": "6 months minimum post-procedure monitoring",
            "travel_restriction": "Not medically cleared for international air travel until September 2025",
            "ongoing_treatment": "Cardiac rehabilitation, medication management, regular cardiology follow-ups",
            "estimated_medical_costs": "$85,000 (hospitalization, procedure, follow-up care)",
            "insurance_coverage": "Partially covered by international insurance, balance paid by applicant",
        }
        
        # Histórico de Viagens
        self.travel_history = {
            # Simplified access fields
            "total_previous_visits": 2,
            "total_time_in_us": "83 days (prior visits)",
            "overstay_record": "None - Perfect compliance",
            "visit_1_entry": "07/10/2023",
            "visit_1_exit": "09/05/2023",
            "visit_1_duration": "57 days",
            "visit_2_entry": "12/20/2022",
            "visit_2_exit": "01/15/2023",
            "visit_2_duration": "26 days",
            
            "us_visits": [
                {
                    "year": "2024-2025",
                    "entry_date": "12/15/2024",
                    "departure_date": "Pending (current visit)",
                    "duration": "158 days (ongoing)",
                    "purpose": "Visit family (daughter and grandchildren)",
                },
                {
                    "year": "2023",
                    "entry_date": "07/10/2023",
                    "departure_date": "09/05/2023",
                    "duration": "57 days",
                    "purpose": "Tourism and family visit",
                },
                {
                    "year": "2022",
                    "entry_date": "12/20/2022",
                    "departure_date": "01/15/2023",
                    "duration": "26 days",
                    "purpose": "Holiday visit with family",
                },
            ],
            "compliance": "Perfect compliance history - always departed on time, never overstayed",
            "other_countries": "Has traveled to Portugal (2021), Argentina (2019), and Chile (2018)",
        }
        
        # Informações do Caso
        self.case_info = {
            "application_date": "May 20, 2025",
            "application_type": "I-539 Extension of Stay",
            "filing_method": "USCIS Lockbox Facility (Paper filing)",
            "filing_fee": "$370",
            "biometrics_fee": "$85 (if required)",
            
            "attorney": {
                "name": "Sarah Johnson, Esq.",
                "bar_number": "FL Bar #987654",
                "law_firm": "Johnson & Associates Immigration Law",
                "address": "800 Brickell Avenue, Suite 500, Miami, FL 33131",
                "phone": "+1 (305) 555-7890",
                "email": "sjohnson@johnsonimmigration.com",
            },
            
            "case_number": "TBD (assigned after filing)",
            "receipt_number": "TBD (assigned after filing)",
        }


# Criar instância do caso
b2_extension_case = B2ExtensionCase()


# Validação básica
def validate_b2_case():
    """Valida dados do caso B-2"""
    issues = []
    
    case = b2_extension_case
    
    # Verificar se aplicação é dentro do prazo
    from datetime import datetime
    
    status_expires = datetime.strptime(case.current_status['current_status_expires'], "%m/%d/%Y")
    filing_date = datetime.strptime(case.extension_request['filing_date'], "%B %d, %Y")
    
    if filing_date > status_expires:
        issues.append("⚠️ WARNING: Filing after status expiration - may face difficulties")
    else:
        days_before = (status_expires - filing_date).days
        if days_before < 45:
            issues.append(f"✅ Filing {days_before} days before expiration - TIMELY")
    
    # Verificar vínculos com país de origem
    if not case.home_country_ties['property']['owns_home']:
        issues.append("⚠️ No property ownership - may weaken case")
    
    if not issues:
        issues.append("✅ Dados validados - sem problemas detectados")
    
    return issues


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODELO DE DADOS - EXTENSÃO DE VISTO B-2")
    print("="*80)
    
    print(f"\n👤 Aplicante: {b2_extension_case.applicant['full_name']}")
    print(f"🎂 Idade: {b2_extension_case.applicant['age']} anos")
    print(f"🛂 Status Atual: {b2_extension_case.current_status['visa_type']}")
    print(f"📅 Data de Entrada: {b2_extension_case.current_status['arrival_date']}")
    print(f"⏰ Expira em: {b2_extension_case.current_status['current_status_expires']}")
    print(f"📝 Aplicação: {b2_extension_case.extension_request['filing_date']}")
    print(f"🎯 Extensão até: {b2_extension_case.extension_request['requested_extension_until']}")
    print(f"\n💡 Razão Principal: {b2_extension_case.extension_request['primary_reason']}")
    
    print("\n" + "="*80)
    print("VALIDAÇÃO DO CASO:")
    print("="*80)
    
    for issue in validate_b2_case():
        print(issue)
    
    print("="*80)
