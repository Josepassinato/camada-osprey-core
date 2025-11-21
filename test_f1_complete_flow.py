#!/usr/bin/env python3
"""
Teste Completo do Fluxo F-1 Student Visa
Testa: API → Supervisor → F1StudentAgent → QA → Métricas
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from visa_specialists.supervisor.supervisor_agent import SupervisorAgent
from f1_student_data_model import f1_student_case

def test_f1_complete_flow():
    """
    Testa fluxo completo de geração de pacote F-1
    """
    print('\n' + '='*80)
    print('🧪 TESTE COMPLETO - F-1 STUDENT VISA PACKAGE')
    print('='*80)
    
    # Dados do estudante
    user_request = """
Preciso de ajuda para preparar minha aplicação de visto F-1 de estudante.
Fui aceito no programa de mestrado em Ciência da Computação na Boston University
e preciso de um pacote completo e profissional para minha entrevista no consulado.
    """
    
    applicant_data = {
        "full_name": f1_student_case.applicant['full_name'],
        "nationality": f1_student_case.applicant['nationality'],
        "program": f1_student_case.us_program['program_name'],
        "school": f1_student_case.us_program['school_name'],
        "start_date": f1_student_case.us_program['start_date']
    }
    
    print(f'\n📋 REQUISIÇÃO DO USUÁRIO:')
    print(f'{user_request.strip()}')
    print(f'\n👤 DADOS DO APLICANTE:')
    print(f'   Nome: {applicant_data["full_name"]}')
    print(f'   Nacionalidade: {applicant_data["nationality"]}')
    print(f'   Programa: {applicant_data["program"]}')
    print(f'   Instituição: {applicant_data["school"]}')
    print(f'   Início: {applicant_data["start_date"]}')
    
    # Inicializar Supervisor
    print(f'\n🎯 INICIANDO SUPERVISOR AGENT...')
    supervisor = SupervisorAgent()
    
    # Processar requisição
    print(f'\n⚙️  PROCESSANDO REQUISIÇÃO...')
    result = supervisor.process_visa_request(
        user_request=user_request,
        applicant_data=applicant_data
    )
    
    # Mostrar resultados
    print(f'\n' + '='*80)
    print(f'📊 RESULTADOS DO PROCESSAMENTO')
    print('='*80)
    
    if result.get('success'):
        print(f'\n✅ STATUS: SUCESSO')
        print(f'\n🎯 Tipo de Visto Identificado: {result.get("visa_type")}')
        print(f'🤖 Agente Especialista: {result.get("specialist_agent")}')
        
        # Package result
        package = result.get('package_result', {})
        if package.get('package_path'):
            print(f'\n📄 PACOTE GERADO:')
            print(f'   Arquivo: {Path(package["package_path"]).name}')
            print(f'   Páginas: {package.get("pages", 0)}')
            print(f'   Tamanho: {package.get("size_kb", 0):.1f} KB')
        
        # Validation
        validation = result.get('validation', {})
        print(f'\n✅ VALIDAÇÃO:')
        print(f'   Válido: {validation.get("is_valid")}')
        print(f'   Score: {validation.get("completeness_score", 0)}%')
        print(f'   Documentos Completos: {validation.get("all_documents_present")}')
        
        # QA Report
        qa = result.get('qa_report', {})
        if qa:
            print(f'\n📋 QA REPORT:')
            print(f'   Overall Score: {qa.get("overall_score", 0)}%')
            print(f'   Passou: {qa.get("passed")}')
            print(f'   Completeness: {qa.get("scores", {}).get("completeness", 0)}%')
            print(f'   Compliance: {qa.get("scores", {}).get("compliance", 0)}%')
            print(f'   Professionalism: {qa.get("scores", {}).get("professionalism", 0)}%')
            print(f'   Accuracy: {qa.get("scores", {}).get("accuracy", 0)}%')
            
            if qa.get('issues'):
                print(f'\n   ⚠️  Issues Encontrados: {len(qa["issues"])}')
                for issue in qa.get('issues', [])[:3]:
                    print(f'      - {issue}')
        
        # Metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f'\n📈 MÉTRICAS:')
            print(f'   Tempo Total: {metrics.get("total_time_seconds", 0):.2f}s')
            print(f'   Documentos Gerados: {metrics.get("documents_generated", 0)}')
        
        # URL para download
        if package.get('package_path'):
            filename = Path(package['package_path']).name
            print(f'\n🔗 LINK PARA DOWNLOAD:')
            print(f'   http://localhost:3000/{filename}')
            print(f'   ou através da API:')
            print(f'   GET /api/visa/download/{filename}')
        
    else:
        print(f'\n❌ STATUS: FALHA')
        print(f'   Erro: {result.get("error")}')
    
    print(f'\n' + '='*80)
    print('🏁 TESTE COMPLETO FINALIZADO')
    print('='*80)
    
    return result


if __name__ == '__main__':
    result = test_f1_complete_flow()
    
    # Return code based on success
    success = result.get('success', False) and result.get('qa_report', {}).get('passed', False)
    exit(0 if success else 1)
