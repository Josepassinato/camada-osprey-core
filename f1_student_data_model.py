#!/usr/bin/env python3
"""
F-1 Student Visa - Modelo de Dados Simulado
Caso realista de estudante brasileiro aplicando para programa de mestrado nos EUA
"""

class F1StudentCase:
    """Dados simulados de estudante F-1"""
    
    def __init__(self):
        # Informações do Estudante
        self.applicant = {
            "full_name": "Rafael Santos Oliveira",
            "given_name": "Rafael Santos",
            "family_name": "Oliveira",
            "dob": "March 15, 1998",
            "dob_formatted": "15/03/1998",
            "age": 26,
            "gender": "M",
            "nationality": "Brazilian",
            "country_of_birth": "Brazil",
            "city_of_birth": "São Paulo",
            "passport_number": "BR123456789",
            "passport_issue_date": "January 10, 2022",
            "passport_expiry_date": "January 9, 2032",
            "passport_country": "Brazil",
            
            # Endereço no Brasil
            "home_address": "Rua Augusta, 1520, Apto 1205",
            "home_city": "São Paulo",
            "home_state": "SP",
            "home_zip": "01304-001",
            "home_country": "Brazil",
            "home_phone": "+55 11 98765-4321",
            "email": "rafael.oliveira@email.com",
            
            # Endereço nos EUA (será com a universidade)
            "us_address": "University Housing - Building A, Room 301",
            "us_city": "Boston",
            "us_state": "Massachusetts",
            "us_zip": "02115",
        }
        
        # Informações Educacionais
        self.education = {
            "highest_degree": "Bachelor's Degree (Graduação)",
            "field_of_study": "Computer Science",
            "institution": "Universidade de São Paulo (USP)",
            "graduation_date": "December 2020",
            "gpa": "3.7/4.0",
            
            "academic_achievements": [
                "Dean's List - 4 semesters",
                "Published research paper on Machine Learning",
                "Winner of University Hackathon 2019",
                "Teaching Assistant for Data Structures course"
            ],
            
            "transcript_summary": {
                "total_credits": 180,
                "major_gpa": "3.8/4.0",
                "relevant_courses": [
                    "Advanced Algorithms",
                    "Machine Learning",
                    "Database Systems",
                    "Software Engineering",
                    "Artificial Intelligence"
                ]
            }
        }
        
        # Programa nos EUA
        self.us_program = {
            "school_name": "Boston University",
            "school_address": "1 Silber Way, Boston, MA 02215",
            "program_name": "Master of Science in Computer Science",
            "program_level": "Graduate (Master's)",
            "sevis_school_code": "BOS214F00567000",
            "start_date": "September 3, 2025",
            "expected_completion": "May 15, 2027",
            "duration": "2 years (4 semesters)",
            "full_time": True,
            "credits_per_semester": 12,
            
            "acceptance_date": "March 1, 2025",
            "acceptance_status": "Unconditional Admission",
            
            "program_description": """
The Master of Science in Computer Science program at Boston University offers 
advanced training in cutting-edge areas of computer science including artificial 
intelligence, machine learning, cybersecurity, and distributed systems. The program 
requires completion of 32 credits over 2 years, including a thesis or capstone project.
            """,
            
            "specialization": "Machine Learning and Artificial Intelligence"
        }
        
        # Form I-20 (emitido pela escola)
        self.i20 = {
            "i20_number": "N0012345678",
            "sevis_id": "N0012345678",
            "issue_date": "March 15, 2025",
            "program_start": "September 3, 2025",
            "program_end": "May 15, 2027",
            "dso_name": "Dr. Jennifer Martinez",
            "dso_title": "International Student Advisor",
            "dso_phone": "+1 (617) 353-3565",
            "school_official_signature": "Jennifer Martinez, DSO",
            
            # Custos (crítico para F-1)
            "tuition_fees": "$32,000 per year",
            "living_expenses": "$18,000 per year",
            "books_supplies": "$1,500 per year",
            "health_insurance": "$2,500 per year",
            "personal_expenses": "$3,000 per year",
            "total_annual_cost": "$57,000 per year",
            "total_program_cost": "$114,000 (2 years)",
            
            "valid_for_entry": "Valid for entry 30 days before September 3, 2025"
        }
        
        # Evidência Financeira (CRÍTICO)
        self.financial_support = {
            "total_required": "$114,000 for 2 years",
            
            "sources": {
                "personal_savings": {
                    "amount": "$45,000",
                    "percentage": "39%",
                    "evidence": "Bank statements from Banco do Brasil"
                },
                "parental_support": {
                    "amount": "$50,000",
                    "percentage": "44%",
                    "evidence": "Parents' bank statements + Affidavit of Support"
                },
                "scholarship": {
                    "amount": "$19,000",
                    "percentage": "17%",
                    "evidence": "Scholarship award letter from Boston University",
                    "details": "Merit-based scholarship, $9,500 per year for 2 years"
                }
            },
            
            "total_available": "$114,000",
            "surplus": "$0",
            
            # Documentos bancários
            "student_bank": {
                "bank_name": "Banco do Brasil",
                "account_type": "Savings Account",
                "account_number": "12345-6",
                "current_balance": "R$ 225,000 (~$45,000 USD)",
                "account_holder": "Rafael Santos Oliveira",
                "statements_period": "October 2024 - March 2025 (6 months)"
            },
            
            "parents_bank": {
                "bank_name": "Itaú Unibanco",
                "account_type": "Joint Savings Account",
                "account_holders": "Carlos Oliveira & Ana Santos Oliveira",
                "current_balance": "R$ 250,000 (~$50,000 USD)",
                "monthly_income": "R$ 35,000 (~$7,000 USD)",
                "statements_period": "October 2024 - March 2025 (6 months)"
            }
        }
        
        # Pais/Sponsors
        self.sponsors = {
            "father": {
                "name": "Carlos Alberto Oliveira",
                "age": 54,
                "occupation": "Civil Engineer / Project Manager",
                "employer": "Construtora ABC Ltda",
                "annual_income": "R$ 210,000 (~$42,000 USD)",
                "relationship": "Father"
            },
            "mother": {
                "name": "Ana Maria Santos Oliveira",
                "age": 52,
                "occupation": "Financial Controller",
                "employer": "XYZ Corporation Brazil",
                "annual_income": "R$ 180,000 (~$36,000 USD)",
                "relationship": "Mother"
            },
            
            "combined_annual_income": "R$ 390,000 (~$78,000 USD)",
            
            "property_owned": {
                "primary_residence": {
                    "address": "Rua Augusta, 1520, Apto 1205, São Paulo, SP",
                    "value": "R$ 1,800,000 (~$360,000 USD)",
                    "ownership": "Fully paid"
                },
                "additional_property": {
                    "address": "Beach apartment in Santos, SP",
                    "value": "R$ 600,000 (~$120,000 USD)",
                    "ownership": "Fully paid"
                }
            }
        }
        
        # Testes de Proficiência em Inglês
        self.english_proficiency = {
            "test": "TOEFL iBT",
            "test_date": "December 10, 2024",
            "overall_score": "105/120",
            "section_scores": {
                "Reading": "28/30",
                "Listening": "27/30",
                "Speaking": "24/30",
                "Writing": "26/30"
            },
            "requirement": "Minimum 90 for Boston University",
            "status": "EXCEEDS REQUIREMENT",
            "test_report_number": "0000123456789",
            
            "alternative_accepted": ["IELTS (min 6.5)", "Duolingo (min 120)"]
        }
        
        # Testes Padronizados (para programa de mestrado)
        self.standardized_tests = {
            "gre": {
                "test_name": "GRE General Test",
                "test_date": "November 15, 2024",
                "verbal": "158/170",
                "quantitative": "168/170",
                "analytical_writing": "4.5/6.0",
                "total": "326/340",
                "percentile": "90th percentile overall",
                "requirement": "Recommended but not required by BU",
                "report_code": "3087 (Boston University)"
            }
        }
        
        # Vínculos com Brasil (Ties to Home Country)
        self.home_country_ties = {
            "family": {
                "parents": "Both parents in São Paulo, Brazil",
                "siblings": "1 sister (age 23) studying dentistry in São Paulo",
                "extended_family": "Grandparents, aunts, uncles in Brazil",
                "all_in_brazil": True
            },
            
            "property": {
                "family_home": "Family owns residential property worth $360,000",
                "student_stake": "Will inherit portion of family assets",
            },
            
            "career_plans": {
                "intent": "Return to Brazil after completing master's degree",
                "reason": "Apply knowledge to Brazil's growing tech industry",
                "job_prospects": "Strong demand for ML engineers in São Paulo",
                "potential_employers": [
                    "Nubank (Brazilian fintech)",
                    "Magazine Luiza (E-commerce)",
                    "Itaú Bank (AI division)",
                    "Brazilian startups"
                ],
                "salary_expectation": "R$ 15,000-20,000/month (3-4x current Brazil wages)",
                "long_term": "Eventually start own tech company in Brazil"
            },
            
            "cultural": "Strong connection to Brazilian culture, family, and community",
            
            "previous_travel": {
                "international": "Visited Argentina (2019), Portugal (2021)",
                "compliance": "Always returned to Brazil",
                "overstays": "None"
            }
        }
        
        # Experiência Profissional (mostra vínculos e qualificação)
        self.work_experience = {
            "current_job": {
                "title": "Junior Software Engineer",
                "company": "Tech Solutions Brazil Ltda",
                "location": "São Paulo, Brazil",
                "start_date": "January 2021",
                "end_date": "Present (will resign before departure)",
                "duration": "4+ years",
                "salary": "R$ 8,000/month (~$1,600 USD/month)",
                "responsibilities": [
                    "Develop machine learning models for client projects",
                    "Backend development using Python and Django",
                    "Database design and optimization",
                    "Code review and mentoring junior developers"
                ],
                "notice": "Will provide 30-day notice before departure for studies"
            },
            
            "relevant_experience": "4 years professional software development experience"
        }
        
        # Razão para Estudar nos EUA
        self.reason_for_usa = {
            "academic": """
Boston University's MS in Computer Science program is ranked among the top 50 in the US 
and offers specialized coursework in machine learning and AI that is not available at this 
level in Brazil. The program's faculty includes leading researchers in AI, and the 
curriculum aligns perfectly with my career goals.
            """,
            
            "career": """
Advanced training in AI/ML from a top US university will provide me with cutting-edge 
knowledge and skills that are in high demand in Brazil's rapidly growing technology sector. 
This degree will enable me to contribute to Brazil's tech industry at a higher level and 
eventually start my own AI-focused company in São Paulo.
            """,
            
            "why_not_brazil": """
While Brazil has good undergraduate programs, graduate programs in AI/ML are limited and 
lack the research facilities, industry partnerships, and faculty expertise available at 
top US universities. The specialized knowledge I'll gain is crucial for my career goals.
            """,
            
            "intent_to_return": """
I have strong family, financial, and professional ties to Brazil. My career goals are 
specifically focused on applying AI technology to solve problems in Brazil's market. 
The US degree is a means to enhance my ability to contribute to Brazil's tech ecosystem, 
not an attempt to immigrate permanently.
            """
        }
        
        # Status de Visto Atual (se aplicável)
        self.current_status = {
            "in_usa": False,
            "current_visa": None,
            "applying_from": "Brazil (Consular Processing)",
            "interview_location": "US Consulate, São Paulo, Brazil",
            "ds160_status": "To be completed after I-20 received"
        }
        
        # SEVIS Fee
        self.sevis_fee = {
            "amount": "$350",
            "status": "To be paid after I-20 received",
            "receipt": "Form I-797 (will be obtained)",
            "validity": "Valid for 12 months or until program start"
        }
        
        # Carta de Recomendação (supporters)
        self.recommendation_letters = {
            "letter_1": {
                "from": "Prof. Dr. Maria Silva",
                "title": "Professor of Computer Science, USP",
                "relationship": "Academic Advisor and Thesis Supervisor",
                "content_summary": "Excellent student, strong research skills, recommended for graduate studies"
            },
            "letter_2": {
                "from": "Dr. João Santos",
                "title": "Senior Software Architect",
                "relationship": "Direct Manager at Tech Solutions Brazil",
                "content_summary": "Outstanding engineer, quick learner, will be valuable asset to any program"
            },
            "letter_3": {
                "from": "Prof. Dr. Carlos Mendes",
                "title": "Department Head, Computer Science, USP",
                "relationship": "Professor and Mentor",
                "content_summary": "Top 5% of students, exceptional analytical skills, highly recommended"
            }
        }


# Instância global para uso
f1_student_case = F1StudentCase()
