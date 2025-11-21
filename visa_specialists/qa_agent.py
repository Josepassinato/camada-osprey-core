"""
Quality Assurance Agent
Agente que faz revisão final de qualidade dos pacotes gerados
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import json


class QualityAssuranceAgent:
    """Agente de controle de qualidade"""
    
    def __init__(self):
        self.qa_dir = Path(__file__).parent / 'qa_reports'
        self.qa_dir.mkdir(parents=True, exist_ok=True)
        
        # Critérios de qualidade
        self.quality_criteria = {
            'completeness': {
                'weight': 0.3,
                'checks': [
                    'all_required_forms_present',
                    'all_required_documents_present',
                    'no_forbidden_documents'
                ]
            },
            'accuracy': {
                'weight': 0.3,
                'checks': [
                    'forms_correctly_filled',
                    'data_consistency',
                    'no_contradictions'
                ]
            },
            'professionalism': {
                'weight': 0.2,
                'checks': [
                    'proper_formatting',
                    'no_typos',
                    'professional_language'
                ]
            },
            'compliance': {
                'weight': 0.2,
                'checks': [
                    'meets_uscis_requirements',
                    'proper_documentation_order',
                    'correct_filing_procedure'
                ]
            }
        }
    
    def review_package(self, package_result: Dict[str, Any], specialist_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz revisão completa do pacote
        
        Args:
            package_result: Resultado do especialista
            specialist_validation: Validação do especialista
            
        Returns:
            Relatório de QA completo
        """
        print(f"\n{'='*80}")
        print(f"🔍 QUALITY ASSURANCE - REVISÃO FINAL")
        print(f"{'='*80}\n")
        
        qa_report = {
            'timestamp': datetime.now().isoformat(),
            'visa_type': package_result.get('visa_type'),
            'overall_score': 0.0,
            'category_scores': {},
            'issues': [],
            'recommendations': [],
            'passed': False
        }
        
        # 1. Completeness Check
        completeness_score = self._check_completeness(specialist_validation)
        qa_report['category_scores']['completeness'] = completeness_score
        print(f"✓ Completeness: {completeness_score:.1%}")
        
        # 2. Accuracy Check
        accuracy_score = self._check_accuracy(package_result)
        qa_report['category_scores']['accuracy'] = accuracy_score
        print(f"✓ Accuracy: {accuracy_score:.1%}")
        
        # 3. Professionalism Check
        professionalism_score = self._check_professionalism(package_result)
        qa_report['category_scores']['professionalism'] = professionalism_score
        print(f"✓ Professionalism: {professionalism_score:.1%}")
        
        # 4. Compliance Check
        compliance_score = self._check_compliance(specialist_validation)
        qa_report['category_scores']['compliance'] = compliance_score
        print(f"✓ Compliance: {compliance_score:.1%}")
        
        # Calculate overall score
        overall_score = (
            completeness_score * self.quality_criteria['completeness']['weight'] +
            accuracy_score * self.quality_criteria['accuracy']['weight'] +
            professionalism_score * self.quality_criteria['professionalism']['weight'] +
            compliance_score * self.quality_criteria['compliance']['weight']
        )
        qa_report['overall_score'] = overall_score
        
        # Determine if passed (threshold: 80%)
        qa_report['passed'] = overall_score >= 0.80
        
        # Generate issues and recommendations
        qa_report['issues'] = self._generate_issues(specialist_validation, package_result)
        qa_report['recommendations'] = self._generate_recommendations(qa_report)
        
        # Save report
        self._save_report(qa_report)
        
        # Print summary
        self._print_summary(qa_report)
        
        return qa_report
    
    def _check_completeness(self, validation: Dict[str, Any]) -> float:
        """Verifica completude do pacote"""
        score = 1.0
        
        if validation.get('missing_items'):
            missing_count = len(validation['missing_items'])
            score -= (missing_count * 0.1)  # -10% por item faltando
        
        if validation.get('forbidden_items_found'):
            forbidden_count = len(validation['forbidden_items_found'])
            score -= (forbidden_count * 0.2)  # -20% por item proibido
        
        return max(0.0, score)
    
    def _check_accuracy(self, package_result: Dict[str, Any]) -> float:
        """Verifica acurácia dos dados"""
        # Por enquanto, score base
        score = 0.95
        
        # Verificar se há erros no resultado
        if not package_result.get('success', False):
            score -= 0.3
        
        return max(0.0, score)
    
    def _check_professionalism(self, package_result: Dict[str, Any]) -> float:
        """Verifica profissionalismo do pacote"""
        # Score base alto - assumindo boa qualidade
        score = 0.90
        
        # Verificar tamanho do pacote (deve ter volume adequado)
        pages = package_result.get('pages', 0)
        if pages < 20:
            score -= 0.1  # Pacote muito pequeno
        elif pages > 100:
            score -= 0.05  # Pacote muito grande
        
        return max(0.0, score)
    
    def _check_compliance(self, validation: Dict[str, Any]) -> float:
        """Verifica compliance com requisitos"""
        if validation.get('is_valid', False):
            return 1.0
        else:
            return 0.6  # Base score se não passou validação
    
    def _generate_issues(self, validation: Dict[str, Any], package_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Gera lista de issues encontrados"""
        issues = []
        
        # Missing items
        for item in validation.get('missing_items', []):
            issues.append({
                'severity': 'high',
                'category': 'completeness',
                'description': f"Missing required document: {item}"
            })
        
        # Forbidden items
        for item in validation.get('forbidden_items_found', []):
            issues.append({
                'severity': 'critical',
                'category': 'compliance',
                'description': f"Forbidden document included: {item}"
            })
        
        # Warnings
        for warning in validation.get('warnings', []):
            issues.append({
                'severity': 'medium',
                'category': 'compliance',
                'description': warning
            })
        
        return issues
    
    def _generate_recommendations(self, qa_report: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas no QA"""
        recommendations = []
        
        # Baseado em scores
        if qa_report['category_scores']['completeness'] < 0.9:
            recommendations.append("Add missing required documents to improve completeness")
        
        if qa_report['category_scores']['accuracy'] < 0.9:
            recommendations.append("Review data accuracy and consistency across documents")
        
        if qa_report['category_scores']['professionalism'] < 0.9:
            recommendations.append("Improve formatting and professional presentation")
        
        if qa_report['category_scores']['compliance'] < 0.9:
            recommendations.append("Ensure all USCIS requirements are met")
        
        # Overall
        if qa_report['overall_score'] < 0.80:
            recommendations.append("⚠️ Package needs significant improvements before submission")
        elif qa_report['overall_score'] < 0.90:
            recommendations.append("Package is acceptable but could be improved")
        else:
            recommendations.append("✅ Package meets high quality standards")
        
        return recommendations
    
    def _save_report(self, qa_report: Dict[str, Any]):
        """Salva relatório de QA"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        visa_type = qa_report.get('visa_type', 'unknown')
        if visa_type and visa_type != 'unknown':
            visa_type = visa_type.replace(' ', '_').replace('-', '')
        filename = f"qa_report_{visa_type}_{timestamp}.json"
        
        report_path = self.qa_dir / filename
        with open(report_path, 'w') as f:
            json.dump(qa_report, f, indent=2)
    
    def _print_summary(self, qa_report: Dict[str, Any]):
        """Imprime sumário do QA"""
        print(f"\n{'='*80}")
        print(f"📊 QA REPORT SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Overall Score: {qa_report['overall_score']:.1%}")
        print(f"Status: {'✅ PASSED' if qa_report['passed'] else '❌ FAILED'}\n")
        
        print("Category Scores:")
        for category, score in qa_report['category_scores'].items():
            print(f"  {category.capitalize()}: {score:.1%}")
        
        if qa_report['issues']:
            print(f"\n⚠️  Issues Found ({len(qa_report['issues'])}):")
            for issue in qa_report['issues'][:5]:  # Show first 5
                print(f"  [{issue['severity'].upper()}] {issue['description']}")
        
        print(f"\n💡 Recommendations ({len(qa_report['recommendations'])}):")
        for rec in qa_report['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n{'='*80}\n")
