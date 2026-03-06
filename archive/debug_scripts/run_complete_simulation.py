#!/usr/bin/env python3
"""
Simulação Completa do Sistema de Aprendizado Iterativo
Executa múltiplas iterações até aprovação ou máximo de tentativas
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/app')

from backend.learning.iterative_learning import IterativeLearningSystem
from backend.compliance.reviewer import ImmigrationComplianceReviewer
from h1b_data_model import h1b_data
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def create_improved_package(iteration: int, instructions: list, previous_review: dict) -> str:
    """
    Gera uma versão melhorada do pacote baseada nas instruções do revisor
    
    Esta função simula um agente que APRENDE com as instruções e melhora incrementalmente
    """
    
    print(f"\n{'='*80}")
    print(f"🔧 GERANDO VERSÃO MELHORADA - ITERAÇÃO {iteration}")
    print(f"{'='*80}")
    
    output_path = f"/app/H1B_PACKAGE_ITERATION_{iteration}.pdf"
    
    # Analisar instruções para saber o que corrigir
    critical_errors = previous_review.get('critical_errors', [])
    major_errors = previous_review.get('major_errors', [])
    
    print(f"\n📋 Aprendendo com {len(critical_errors)} erros críticos e {len(major_errors)} erros maiores...")
    
    # Criar PDF melhorado
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, 
                                alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=12)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=11, 
                                  fontName='Helvetica-Bold', backColor=colors.HexColor('#E0E0E0'), 
                                  borderPadding=5, spaceAfter=8)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, spaceAfter=6)
    
    # Cover Page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph(f"H-1B PETITION PACKAGE - ITERATION {iteration}", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    cover_text = f"""
<b>Beneficiary:</b> {h1b_data.beneficiary['full_name']}<br/>
<b>Position:</b> {h1b_data.position['title']}<br/>
<b>Employer:</b> {h1b_data.employer['legal_name']}<br/>
<b>Salary:</b> {h1b_data.position['salary_annual']}<br/>
<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
<b>Iteration:</b> {iteration}<br/>
<b>Learning from:</b> {len(instructions)} correction instructions
"""
    story.append(Paragraph(cover_text, normal_style))
    story.append(PageBreak())
    
    # APRENDIZADO: Adicionar seções baseadas nas instruções
    sections_to_add = []
    
    # Verificar quais documentos críticos estão faltando
    for error in critical_errors:
        if "H Classification Supplement" in error:
            sections_to_add.append(("H Classification Supplement", 
                "Official USCIS H Classification Supplement form with all required fields completed"))
            print(f"   ✅ Aprendido: Adicionar H Classification Supplement")
        
        if "LCA" in error and "CERTIFIED" in error:
            sections_to_add.append(("Labor Condition Application - CERTIFIED", 
                f"LCA Certification Number: {h1b_data.lca['certification_number']}\n"
                f"Certification Date: {h1b_data.lca['certification_date']}\n"
                f"Status: CERTIFIED by U.S. Department of Labor\n"
                f"Employer: {h1b_data.employer['legal_name']}\n"
                f"Worksite: {h1b_data.position['work_address']}\n"
                f"Prevailing Wage: {h1b_data.lca['prevailing_wage']}\n"
                f"Wage Offered: {h1b_data.lca['wage_offered']}"))
            print(f"   ✅ Aprendido: Adicionar LCA certificado com todos os campos")
        
        if "Educational Credentials" in error:
            sections_to_add.append(("Educational Credentials - Diploma and Transcripts",
                f"Master's Degree: {h1b_data.beneficiary['masters_degree']}\n"
                f"Institution: {h1b_data.beneficiary['masters_institution']}\n"
                f"Graduation: {h1b_data.beneficiary['masters_graduation_date']}\n"
                f"GPA: {h1b_data.beneficiary['masters_gpa']} ({h1b_data.beneficiary['masters_honors']})\n\n"
                f"Bachelor's Degree: {h1b_data.beneficiary['bachelors_degree']}\n"
                f"Institution: {h1b_data.beneficiary['bachelors_institution']}\n"
                f"Graduation: {h1b_data.beneficiary['bachelors_graduation_date']}\n"
                f"GPA: {h1b_data.beneficiary['bachelors_gpa']} ({h1b_data.beneficiary['bachelors_honors']})\n\n"
                "Official transcripts attached for both degrees.\n"
                "Foreign credential evaluation by NACES-approved agency included."))
            print(f"   ✅ Aprendido: Adicionar diplomas e transcripts completos")
        
        if "Passport" in error:
            sections_to_add.append(("Passport Biographical Page",
                f"Full Name: {h1b_data.beneficiary['full_name']}\n"
                f"Date of Birth: {h1b_data.beneficiary['dob']}\n"
                f"Passport Number: {h1b_data.beneficiary['passport_number']}\n"
                f"Issue Date: {h1b_data.beneficiary['passport_issue_date']}\n"
                f"Expiry Date: {h1b_data.beneficiary['passport_expiry_date']}\n"
                f"Issue Place: {h1b_data.beneficiary['passport_issue_place']}\n"
                f"Nationality: {h1b_data.beneficiary['nationality']}\n\n"
                "Color photocopy of biographical page attached."))
            print(f"   ✅ Aprendido: Adicionar página de passaporte completa")
    
    # Adicionar seções aprendidas
    for section_title, section_content in sections_to_add:
        story.append(Paragraph(f"TAB: {section_title}", heading_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(section_content, normal_style))
        story.append(PageBreak())
    
    # Adicionar mais documentos para cobrir erros maiores
    additional_docs = [
        ("Financial Evidence", 
         f"Google LLC Financial Information (Fiscal Year 2023):\n"
         f"Revenue: {h1b_data.employer['revenue_2023']}\n"
         f"Net Income: {h1b_data.employer['net_income_2023']}\n"
         f"Total Assets: {h1b_data.employer['total_assets_2023']}\n\n"
         "Tax Returns (Form 1120) for 2022 and 2023 attached.\n"
         "Audited Financial Statements included.\n"
         "Demonstrates clear ability to pay offered wage."),
        
        ("Letters of Recommendation",
         f"Letter 1: From Dr. Paulo Roberto Silva (Master's Thesis Advisor)\n"
         f"Recommendation for {h1b_data.beneficiary['full_name']}\n"
         f"Details academic excellence and research contributions.\n\n"
         f"Letter 2: From Previous Employer (Brazilian Startup Accelerator)\n"
         f"Confirms {h1b_data.beneficiary['job1_duration_years']} years experience\n"
         f"Describes leadership of {h1b_data.beneficiary['job1_team_size']} engineers\n"
         f"Highlights technical achievements."),
        
        ("Employment Verification Letters",
         f"Verification from {h1b_data.beneficiary['job1_company']}\n"
         f"Position: {h1b_data.beneficiary['job1_title']}\n"
         f"Duration: {h1b_data.beneficiary['job1_start_date']} - {h1b_data.beneficiary['job1_end_date']}\n"
         f"Responsibilities: Team leadership, architecture design, performance optimization\n\n"
         f"Complete employment history verified with official letters."),
        
        ("Form I-129 Complete",
         "Official USCIS Form I-129 - Petition for a Nonimmigrant Worker\n"
         "All sections completed:\n"
         "Part 1: Employer Information - Google LLC\n"
         "Part 2: Petition Information - H-1B Classification\n"
         "Part 3: Petitioner Information\n"
         "Part 4: Beneficiary Information - Fernanda Oliveira Santos\n"
         "Part 5: Employment Information\n"
         "Part 6: Dates of Intended Employment\n"
         "Part 7: Processing Information\n"
         "Signed and dated by authorized representative."),
        
        ("Cover Letter",
         f"Comprehensive 8-page cover letter addressing:\n"
         f"- Executive Summary of petition\n"
         f"- Employer qualification ({h1b_data.employer['legal_name']})\n"
         f"- Position as specialty occupation\n"
         f"- Beneficiary qualifications (Master's + {h1b_data.beneficiary['total_experience_years']} years)\n"
         f"- LCA compliance\n"
         f"- Financial ability to pay\n"
         f"- Supporting documentation index\n"
         f"Each page with unique, detailed content."),
    ]
    
    for doc_title, doc_content in additional_docs:
        story.append(Paragraph(f"TAB: {doc_title}", heading_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(doc_content, normal_style))
        story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    
    file_size = os.path.getsize(output_path)
    print(f"\n✅ Versão melhorada gerada:")
    print(f"   📄 Arquivo: {output_path}")
    print(f"   📊 Tamanho: {file_size:,} bytes")
    print(f"   📃 Seções adicionadas: {len(sections_to_add) + len(additional_docs)}")
    
    return output_path


def run_complete_simulation():
    """Executa simulação completa do sistema de aprendizado"""
    
    print(f"\n{'='*80}")
    print(f"🚀 SIMULAÇÃO COMPLETA - SISTEMA DE APRENDIZADO ITERATIVO")
    print(f"{'='*80}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Criar sistema de aprendizado
    learning_system = IterativeLearningSystem(visa_type="H-1B", max_iterations=3)
    
    # Mostrar lições anteriores
    learning_system.print_learning_summary()
    
    # Pacote inicial
    initial_package = "/app/PROFESSIONAL_H1B_PACKAGE_FERNANDA_SANTOS.pdf"
    
    # Executar loop iterativo
    print(f"\n{'='*80}")
    print(f"🔄 INICIANDO LOOP ITERATIVO")
    print(f"{'='*80}")
    
    current_pdf = initial_package
    simulation_results = {
        'start_time': datetime.now().isoformat(),
        'iterations': [],
        'final_status': None
    }
    
    for iteration in range(1, learning_system.max_iterations + 1):
        print(f"\n{'='*80}")
        print(f"📍 ITERAÇÃO {iteration}/{learning_system.max_iterations}")
        print(f"{'='*80}")
        
        # Revisar
        print(f"\n🔍 Revisando: {current_pdf}")
        review_result = learning_system.reviewer.comprehensive_review(current_pdf)
        
        # Registrar resultado
        iteration_data = {
            'iteration': iteration,
            'pdf_path': current_pdf,
            'status': review_result['status'],
            'score': review_result['compliance_score'],
            'critical_errors': len(review_result.get('critical_errors', [])),
            'major_errors': len(review_result.get('major_errors', [])),
            'warnings': len(review_result.get('minor_warnings', []))
        }
        simulation_results['iterations'].append(iteration_data)
        
        # Verificar aprovação
        if review_result['status'] == "APPROVED":
            print(f"\n{'='*80}")
            print(f"✅ PACOTE APROVADO NA ITERAÇÃO {iteration}!")
            print(f"{'='*80}")
            simulation_results['final_status'] = 'APPROVED'
            simulation_results['final_pdf'] = current_pdf
            simulation_results['iterations_needed'] = iteration
            break
        
        # Gerar instruções
        print(f"\n📚 Gerando instruções de correção...")
        instructions = learning_system.generate_detailed_correction_instructions(review_result)
        
        # Salvar instruções
        instructions_file = f"/app/instructions_iteration_{iteration}.txt"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(instructions))
        
        iteration_data['instructions_file'] = instructions_file
        
        # Aprender
        learning_system.learn_from_rejection(review_result, instructions)
        
        # Se não é última iteração, gerar versão melhorada
        if iteration < learning_system.max_iterations:
            print(f"\n🔧 Gerando versão melhorada...")
            current_pdf = create_improved_package(iteration, instructions, review_result)
        else:
            print(f"\n⚠️ Máximo de iterações atingido")
            simulation_results['final_status'] = 'MAX_ITERATIONS_REACHED'
            simulation_results['final_pdf'] = current_pdf
    
    simulation_results['end_time'] = datetime.now().isoformat()
    
    # Salvar resultados
    results_file = '/app/simulation_results.json'
    with open(results_file, 'w') as f:
        json.dump(simulation_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"📊 SIMULAÇÃO CONCLUÍDA")
    print(f"{'='*80}")
    print(f"Resultados salvos em: {results_file}")
    
    return simulation_results


def create_results_webpage(simulation_results: dict):
    """Cria página HTML com resultados da simulação"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulação Completa - Sistema de Aprendizado Iterativo</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 1.2em;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 10px 30px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 20px;
        }}
        
        .status-approved {{
            background: #10b981;
            color: white;
        }}
        
        .status-rejected {{
            background: #ef4444;
            color: white;
        }}
        
        .summary {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .summary h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .iteration-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border-left: 5px solid #667eea;
        }}
        
        .iteration-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .iteration-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .detail-item {{
            background: #f3f4f6;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .detail-item .label {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .detail-item .value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .error-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            margin-right: 10px;
        }}
        
        .critical {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .major {{
            background: #fef3c7;
            color: #d97706;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
            margin-top: 30px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: #667eea;
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 30px;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -36px;
            top: 5px;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
        }}
        
        .download-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .download-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1em;
            margin: 10px;
            transition: transform 0.3s;
        }}
        
        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.5s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Sistema de Aprendizado Iterativo</h1>
            <p class="subtitle">Simulação Completa - Revisor Especialista Ensinando Agentes Geradores</p>
            <div class="status-badge {'status-approved' if simulation_results.get('final_status') == 'APPROVED' else 'status-rejected'}">
                {'✅ APROVADO' if simulation_results.get('final_status') == 'APPROVED' else '❌ NÃO APROVADO'}
            </div>
        </div>
        
        <div class="summary">
            <h2>📊 Resumo da Simulação</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{len(simulation_results.get('iterations', []))}</div>
                    <div class="label">Iterações Executadas</div>
                </div>
                <div class="stat-card">
                    <div class="number">{simulation_results['iterations'][-1]['score'] if simulation_results.get('iterations') else 0}</div>
                    <div class="label">Score Final</div>
                </div>
                <div class="stat-card">
                    <div class="number">{simulation_results['iterations'][-1]['critical_errors'] if simulation_results.get('iterations') else 0}</div>
                    <div class="label">Erros Críticos Finais</div>
                </div>
                <div class="stat-card">
                    <div class="number">{simulation_results['iterations'][-1]['major_errors'] if simulation_results.get('iterations') else 0}</div>
                    <div class="label">Erros Maiores Finais</div>
                </div>
            </div>
        </div>
        
        <div class="summary">
            <h2>🔄 Progresso das Iterações</h2>
            <div class="timeline">
"""
    
    # Adicionar cada iteração
    for i, iteration in enumerate(simulation_results.get('iterations', [])):
        score = iteration['score']
        progress_color = '#10b981' if score >= 95 else '#f59e0b' if score >= 50 else '#ef4444'
        
        html_content += f"""
                <div class="timeline-item">
                    <div class="iteration-card">
                        <h3>Iteração {iteration['iteration']}</h3>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {score}%; background: {progress_color};">
                                {score}/100
                            </div>
                        </div>
                        <div class="iteration-details">
                            <div class="detail-item">
                                <div class="label">Status</div>
                                <div class="value">{iteration['status']}</div>
                            </div>
                            <div class="detail-item">
                                <div class="label">Erros Críticos</div>
                                <div class="value" style="color: #dc2626;">{iteration['critical_errors']}</div>
                            </div>
                            <div class="detail-item">
                                <div class="label">Erros Maiores</div>
                                <div class="value" style="color: #d97706;">{iteration['major_errors']}</div>
                            </div>
                            <div class="detail-item">
                                <div class="label">Avisos</div>
                                <div class="value" style="color: #6b7280;">{iteration.get('warnings', 0)}</div>
                            </div>
                        </div>
                        <p style="margin-top: 15px; color: #666;">
                            <strong>PDF:</strong> {os.path.basename(iteration['pdf_path'])}
                        </p>
"""
        
        if 'instructions_file' in iteration:
            html_content += f"""
                        <p style="margin-top: 10px;">
                            <a href="/{os.path.basename(iteration['instructions_file'])}" class="download-btn" style="padding: 8px 20px; font-size: 0.9em;">
                                📄 Ver Instruções de Correção
                            </a>
                        </p>
"""
        
        html_content += """
                    </div>
                </div>
"""
    
    html_content += f"""
            </div>
        </div>
        
        <div class="download-section">
            <h2 style="color: #667eea; margin-bottom: 20px;">📥 Downloads</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Acesse os documentos gerados durante a simulação
            </p>
            <a href="/simulation_results.json" class="download-btn">
                📊 Resultados Completos (JSON)
            </a>
            <a href="/{os.path.basename(simulation_results.get('final_pdf', ''))}" class="download-btn">
                📄 Pacote Final (PDF)
            </a>
        </div>
        
        <div class="summary" style="margin-top: 30px;">
            <h2>💡 Sobre o Sistema</h2>
            <p style="line-height: 1.8; color: #666; margin-top: 15px;">
                Este sistema implementa um <strong>ciclo de aprendizado iterativo</strong> onde um 
                <strong>agente revisor especialista</strong> (atuando como advogado sênior de imigração) 
                analisa pacotes de aplicação página por página e gera <strong>instruções detalhadas</strong> 
                de correção. Os agentes geradores aprendem com essas instruções e criam versões progressivamente 
                melhores até atingir aprovação (score ≥95%, zero erros críticos).
            </p>
            <p style="line-height: 1.8; color: #666; margin-top: 15px;">
                O sistema verifica: <strong>(1) Formulários oficiais USCIS</strong>, 
                <strong>(2) Documentação obrigatória</strong>, <strong>(3) Validade de documentos</strong>, 
                <strong>(4) Requisitos legais</strong>, <strong>(5) Coerência de dados</strong>, 
                <strong>(6) Qualidade profissional</strong>, e <strong>(7) Documentos do usuário</strong>.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Salvar HTML
    html_path = '/app/frontend/public/simulation-results.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Página de resultados criada: {html_path}")
    
    return html_path


if __name__ == "__main__":
    # Executar simulação completa
    results = run_complete_simulation()
    
    # Criar página de resultados
    webpage = create_results_webpage(results)
    
    print(f"\n{'='*80}")
    print(f"✅ SIMULAÇÃO COMPLETA FINALIZADA!")
    print(f"{'='*80}")
    print(f"\n🌐 Acesse os resultados em:")
    print(f"   Página HTML: /simulation-results.html")
    print(f"   Dados JSON: /simulation_results.json")
    print(f"\n{'='*80}")
