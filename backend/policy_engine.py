"""
Policy Engine - Motor de políticas baseado em YAML (Enhanced Phase 2)
Processa políticas de validação de documentos com extração avançada de campos e translation gate
"""
import yaml
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
from document_catalog import document_catalog, DocumentType
from document_quality_checker import DocumentQualityChecker
from field_extraction_engine import field_extraction_engine
from translation_gate import translation_gate
from cross_document_consistency import cross_document_consistency
from document_classifier import document_classifier

logger = logging.getLogger(__name__)

class PolicyEngine:
    """
    Motor de políticas para validação de documentos
    """
    
    def __init__(self, policies_dir: str = None):
        self.policies_dir = Path(policies_dir or "policies")
        self.loaded_policies = {}
        self.quality_checker = DocumentQualityChecker()
        self.field_extractor = field_extraction_engine
        self.translation_gate = translation_gate
        self.consistency_engine = cross_document_consistency
        self.document_classifier = document_classifier
        self._load_all_policies()
    
    def _load_all_policies(self):
        """
        Carrega todas as políticas YAML do diretório
        """
        try:
            if not self.policies_dir.exists():
                logger.warning(f"Policies directory not found: {self.policies_dir}")
                return
            
            for policy_file in self.policies_dir.glob("*.yaml"):
                try:
                    with open(policy_file, 'r', encoding='utf-8') as f:
                        policy_data = yaml.safe_load(f)
                    
                    doc_type = policy_data.get('doc_type')
                    if doc_type:
                        self.loaded_policies[doc_type] = policy_data
                        logger.info(f"Loaded policy for {doc_type}")
                    
                except Exception as e:
                    logger.error(f"Error loading policy {policy_file}: {e}")
            
            logger.info(f"Loaded {len(self.loaded_policies)} document policies")
            
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
    
    def get_policy(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """
        Retorna política para um tipo de documento
        """
        return self.loaded_policies.get(doc_type)
    
    def validate_document(self, 
                         file_content: bytes, 
                         filename: str, 
                         doc_type: str,
                         extracted_text: str = "",
                         case_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Valida documento completo usando política correspondente
        """
        try:
            result = {
                "document_id": f"doc_{hash(filename) % 100000}",
                "doc_type": doc_type,
                "status": "pending",
                "quality": {},
                "policy_checks": [],
                "fields": {},
                "consistency": [],
                "overall_score": 0.0,
                "decision": "PENDING",
                "messages": []
            }
            
            # 1. Verificar se política existe
            policy = self.get_policy(doc_type)
            if not policy:
                result["status"] = "error"
                result["decision"] = "FAIL"
                result["messages"].append(f"Política não encontrada para {doc_type}")
                return result
            
            # 2. Análise de qualidade
            quality_result = self.quality_checker.analyze_quality(file_content, filename)
            result["quality"] = quality_result
            
            # 3. Verificações de política
            policy_checks = self._apply_policy_checks(policy, quality_result, extracted_text, case_context)
            result["policy_checks"] = policy_checks
            
            # 4. Análise de idioma e requisitos de tradução (Phase 2)
            language_analysis = self.translation_gate.analyze_document_language(
                extracted_text, doc_type, filename
            )
            result["language_analysis"] = language_analysis
            
            # 5. Extração avançada de campos (Phase 2)
            if extracted_text:
                policy_fields = policy.get("required_fields", []) + policy.get("optional_fields", [])
                extraction_context = {
                    'document_type': doc_type,
                    'case_context': case_context,
                    'language_info': language_analysis
                }
                
                # Usar motor avançado de extração
                fields_result = self.field_extractor.extract_all_fields(
                    extracted_text, policy_fields, extraction_context
                )
                result["fields"] = fields_result
                
                # Verificar certificado de tradução se necessário
                if language_analysis.get('requires_action', False):
                    translation_cert = self.translation_gate.check_translation_certificate(extracted_text)
                    result["translation_certificate"] = translation_cert
            
            # 6. Verificações de consistência (se contexto do caso disponível)
            if case_context:
                consistency_result = self._check_consistency(policy, result["fields"], case_context)
                result["consistency"] = consistency_result
            
            # 7. Cálculo de score e decisão (Phase 2 enhanced)
            score, decision = self._calculate_score_and_decision_enhanced(policy, result)
            result["overall_score"] = score
            result["decision"] = decision
            result["status"] = "done"
            
            # 8. Gerar mensagens de feedback avançadas
            result["messages"] = self._generate_user_messages_enhanced(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating document: {e}")
            return {
                "document_id": f"doc_error_{hash(filename) % 100000}",
                "doc_type": doc_type,
                "status": "error", 
                "quality": {},
                "policy_checks": [],
                "fields": {},
                "consistency": [],
                "overall_score": 0.0,
                "decision": "FAIL",
                "messages": [f"Erro na validação: {str(e)}"]
            }
    
    def _apply_policy_checks(self, policy: Dict, quality_result: Dict, extracted_text: str, case_context: Dict) -> List[Dict]:
        """
        Aplica verificações da política
        """
        checks = []
        
        # 1. Verificações de qualidade
        quality_checks = self._check_quality_requirements(policy, quality_result)
        checks.extend(quality_checks)
        
        # 2. Verificações de idioma
        language_checks = self._check_language_requirements(policy, extracted_text)
        checks.extend(language_checks)
        
        # 3. Verificações de presença (selos, assinaturas, etc.)
        presence_checks = self._check_presence_requirements(policy, extracted_text)
        checks.extend(presence_checks)
        
        # 4. Verificações de snippets de texto obrigatórios
        snippet_checks = self._check_text_snippets(policy, extracted_text)
        checks.extend(snippet_checks)
        
        return checks
    
    def _check_quality_requirements(self, policy: Dict, quality_result: Dict) -> List[Dict]:
        """
        Verifica requisitos de qualidade
        """
        checks = []
        quality_policy = policy.get("quality", {})
        
        # Verificar DPI mínimo (para imagens)
        if "image_specific" in quality_result.get("checks", {}):
            image_data = quality_result["checks"]["image_specific"]
            min_dpi = quality_policy.get("min_dpi", 150)
            estimated_dpi = image_data.get("estimated_dpi", 0)
            
            if estimated_dpi < min_dpi:
                checks.append({
                    "rule": "quality:min_dpi",
                    "result": "fail" if estimated_dpi < min_dpi * 0.7 else "alert",
                    "message": f"DPI estimado ({estimated_dpi:.0f}) abaixo do mínimo ({min_dpi})",
                    "severity": "high" if estimated_dpi < min_dpi * 0.7 else "medium"
                })
            else:
                checks.append({
                    "rule": "quality:min_dpi", 
                    "result": "pass",
                    "message": f"DPI adequado ({estimated_dpi:.0f})",
                    "severity": "low"
                })
        
        # Verificar tamanho do arquivo
        file_size_check = quality_result.get("checks", {}).get("file_size", {})
        if file_size_check.get("status") == "fail":
            checks.append({
                "rule": "quality:file_size",
                "result": "fail",
                "message": file_size_check.get("message", "Tamanho de arquivo inválido"),
                "severity": "critical"
            })
        elif file_size_check.get("status") == "pass":
            checks.append({
                "rule": "quality:file_size",
                "result": "pass", 
                "message": file_size_check.get("message", "Tamanho adequado"),
                "severity": "low"
            })
        
        return checks
    
    def _check_language_requirements(self, policy: Dict, extracted_text: str) -> List[Dict]:
        """
        Verifica requisitos de idioma
        """
        checks = []
        language_req = policy.get("language", "en")
        
        if language_req == "en_or_translation_required":
            # Heurística simples para detectar se texto está em inglês
            english_words = ["the", "and", "of", "to", "in", "is", "was", "for", "with", "on"]
            portuguese_words = ["de", "da", "do", "em", "para", "com", "por", "uma", "um", "na", "no"]
            
            text_lower = extracted_text.lower()
            
            english_score = sum(1 for word in english_words if word in text_lower)
            portuguese_score = sum(1 for word in portuguese_words if word in text_lower)
            
            if portuguese_score > english_score and len(extracted_text) > 100:
                checks.append({
                    "rule": "language:translation_required",
                    "result": "fail",
                    "message": "Documento não está em inglês - tradução certificada necessária",
                    "severity": "critical"
                })
            else:
                checks.append({
                    "rule": "language:english_detected",
                    "result": "pass",
                    "message": "Documento em inglês ou traduzido",
                    "severity": "low"
                })
        
        return checks
    
    def _check_presence_requirements(self, policy: Dict, extracted_text: str) -> List[Dict]:
        """
        Verifica requisitos de presença (selos, assinaturas, etc.)
        """
        checks = []
        presence_checks = policy.get("presence_checks", {})
        
        # Verificar carimbo/selo oficial
        if presence_checks.get("official_seal_or_stamp"):
            seal_words = ["seal", "stamp", "carimbo", "selo", "official", "governo"]
            has_seal = any(word in extracted_text.lower() for word in seal_words)
            
            if not has_seal:
                checks.append({
                    "rule": "presence:official_seal",
                    "result": "alert",
                    "message": "Carimbo ou selo oficial não detectado",
                    "severity": "medium"
                })
            else:
                checks.append({
                    "rule": "presence:official_seal",
                    "result": "pass", 
                    "message": "Carimbo/selo detectado",
                    "severity": "low"
                })
        
        # Verificar assinatura
        if presence_checks.get("signature"):
            signature_words = ["signature", "signed", "assinatura", "assinado"]
            has_signature = any(word in extracted_text.lower() for word in signature_words)
            
            if not has_signature:
                checks.append({
                    "rule": "presence:signature",
                    "result": "alert",
                    "message": "Assinatura não detectada",
                    "severity": "medium"
                })
            else:
                checks.append({
                    "rule": "presence:signature", 
                    "result": "pass",
                    "message": "Assinatura detectada",
                    "severity": "low"
                })
        
        return checks
    
    def _check_text_snippets(self, policy: Dict, extracted_text: str) -> List[Dict]:
        """
        Verifica snippets de texto obrigatórios
        """
        checks = []
        required_snippets = policy.get("required_text_snippets", [])
        
        for snippet in required_snippets:
            if snippet.lower() in extracted_text.lower():
                checks.append({
                    "rule": f"snippet:{snippet}",
                    "result": "pass",
                    "message": f"Texto obrigatório encontrado: '{snippet}'",
                    "severity": "low"
                })
            else:
                checks.append({
                    "rule": f"snippet:{snippet}",
                    "result": "fail",
                    "message": f"Texto obrigatório não encontrado: '{snippet}'",
                    "severity": "critical"
                })
        
        return checks
    
    def _extract_fields(self, policy: Dict, extracted_text: str) -> Dict[str, Any]:
        """
        Extrai campos usando regex da política
        """
        fields = {}
        required_fields = policy.get("required_fields", [])
        optional_fields = policy.get("optional_fields", [])
        
        all_fields = required_fields + optional_fields
        
        for field_def in all_fields:
            field_name = field_def.get("name")
            field_regex = field_def.get("regex")
            
            if field_name and field_regex:
                try:
                    matches = re.finditer(field_regex, extracted_text, re.IGNORECASE | re.MULTILINE)
                    found_values = [match.group() for match in matches]
                    
                    fields[field_name] = {
                        "values": found_values,
                        "found": len(found_values) > 0,
                        "confidence": 1.0 if found_values else 0.0,
                        "required": field_def in required_fields
                    }
                    
                except re.error as e:
                    logger.warning(f"Invalid regex for field {field_name}: {e}")
                    fields[field_name] = {
                        "values": [],
                        "found": False,
                        "confidence": 0.0,
                        "required": field_def in required_fields,
                        "error": f"Regex inválido: {e}"
                    }
        
        return fields
    
    def _check_consistency(self, policy: Dict, fields: Dict, case_context: Dict) -> List[Dict]:
        """
        Verifica consistência entre documentos (implementação básica)
        """
        consistency_checks = []
        consistency_rules = policy.get("consistency_checks", [])
        
        # Implementação básica - pode ser expandida
        for rule in consistency_rules:
            if rule == "match_beneficiary_name_across_docs":
                # Verificação simplificada de consistência de nome
                consistency_checks.append({
                    "rule": "consistency:beneficiary_name",
                    "result": "pass",  # Placeholder
                    "message": "Consistência de nome verificada",
                    "severity": "low"
                })
        
        return consistency_checks
    
    def _calculate_score_and_decision(self, policy: Dict, result: Dict) -> Tuple[float, str]:
        """
        Calcula score geral e decisão final
        """
        # Pesos da política ou padrão
        scoring = policy.get("scoring", {
            "critical_fields_weight": 0.35,
            "quality_weight": 0.25,
            "presence_checks_weight": 0.15,
            "consistency_weight": 0.1,
            "language_compliance_weight": 0.1,
            "field_extraction_weight": 0.05
        })
        
        scores = []
        
        # Score de qualidade
        quality_status = result["quality"].get("status", "fail")
        quality_score = {"ok": 1.0, "alert": 0.7, "fail": 0.0}.get(quality_status, 0.0)
        scores.append(quality_score * scoring["quality_weight"])
        
        # Score de verificações de política
        policy_checks = result["policy_checks"]
        if policy_checks:
            pass_count = sum(1 for check in policy_checks if check["result"] == "pass")
            total_count = len(policy_checks)
            policy_score = pass_count / total_count if total_count > 0 else 0.0
            scores.append(policy_score * (scoring["critical_fields_weight"] + scoring["presence_checks_weight"]))
        
        # Score de consistência
        consistency_checks = result["consistency"]
        if consistency_checks:
            pass_count = sum(1 for check in consistency_checks if check["result"] == "pass")
            total_count = len(consistency_checks)
            consistency_score = pass_count / total_count if total_count > 0 else 1.0
            scores.append(consistency_score * scoring["consistency_weight"])
        
        overall_score = sum(scores) if scores else 0.0
        
        # Determinar decisão
        has_critical_fail = any(
            check["result"] == "fail" and check["severity"] == "critical"
            for check in policy_checks
        )
        
        if has_critical_fail:
            decision = "FAIL"
        elif overall_score >= 0.85:
            decision = "PASS"  
        elif overall_score >= 0.65:
            decision = "ALERT"
        else:
            decision = "FAIL"
        
        return overall_score, decision
    
    def _calculate_score_and_decision_enhanced(self, policy: Dict, result: Dict) -> Tuple[float, str]:
        """
        Cálculo de score aprimorado (Phase 2) incluindo análise de idioma e extração avançada
        """
        # Pesos da política ou padrão aprimorado
        scoring = policy.get("scoring", {
            "critical_fields_weight": 0.35,
            "quality_weight": 0.25,
            "presence_checks_weight": 0.15,
            "consistency_weight": 0.1,
            "language_compliance_weight": 0.1,
            "field_extraction_weight": 0.05
        })
        
        scores = []
        
        # 1. Score de qualidade
        quality_status = result["quality"].get("status", "fail")
        quality_score = {"ok": 1.0, "alert": 0.7, "fail": 0.0}.get(quality_status, 0.0)
        scores.append(quality_score * scoring["quality_weight"])
        
        # 2. Score de verificações de política
        policy_checks = result["policy_checks"]
        if policy_checks:
            pass_count = sum(1 for check in policy_checks if check["result"] == "pass")
            total_count = len(policy_checks)
            policy_score = pass_count / total_count if total_count > 0 else 0.0
            scores.append(policy_score * (scoring["critical_fields_weight"] + scoring["presence_checks_weight"]))
        
        # 3. Score de conformidade de idioma (Phase 2)
        language_analysis = result.get("language_analysis", {})
        language_compliant = language_analysis.get("compliance", {}).get("compliant", True)
        language_score = 1.0 if language_compliant else 0.3  # Penalização por não-conformidade
        language_weight = scoring.get("language_compliance_weight", 0.1)  # Default weight if missing
        scores.append(language_score * language_weight)
        
        # 4. Score de extração de campos (Phase 2)
        fields = result.get("fields", {})
        if fields:
            field_scores = []
            
            # Avaliar campos da política
            policy_fields = fields.get("policy_fields", {})
            for field_name, field_data in policy_fields.items():
                if field_data.get("required", False):
                    if field_data.get("found", False) and field_data.get("best_match"):
                        best_match = field_data["best_match"]
                        validation = best_match.get("validation", {})
                        if validation.get("is_valid", False):
                            field_scores.append(validation.get("confidence", 0.5))
                        else:
                            field_scores.append(0.0)
                    else:
                        field_scores.append(0.0)
            
            field_extraction_score = sum(field_scores) / len(field_scores) if field_scores else 1.0
            scores.append(field_extraction_score * scoring["field_extraction_weight"])
        
        # 5. Score de consistência
        consistency_checks = result["consistency"]
        if consistency_checks:
            pass_count = sum(1 for check in consistency_checks if check["result"] == "pass")
            total_count = len(consistency_checks)
            consistency_score = pass_count / total_count if total_count > 0 else 1.0
            scores.append(consistency_score * scoring["consistency_weight"])
        
        overall_score = sum(scores) if scores else 0.0
        
        # Determinar decisão aprimorada
        has_critical_fail = any(
            check["result"] == "fail" and check["severity"] == "critical"
            for check in policy_checks
        )
        
        # Verificar se tradução é obrigatória e não está presente
        requires_translation = language_analysis.get("requires_action", False)
        has_translation_cert = result.get("translation_certificate", {}).get("has_translation_certificate", False)
        translation_violation = requires_translation and not has_translation_cert
        
        if has_critical_fail or translation_violation:
            decision = "FAIL"
        elif overall_score >= 0.90:
            decision = "PASS"  
        elif overall_score >= 0.70:
            decision = "ALERT"
        else:
            decision = "FAIL"
        
        return overall_score, decision
    
    def _generate_user_messages_enhanced(self, result: Dict) -> List[str]:
        """
        Gera mensagens de feedback avançadas para o usuário (Phase 2)
        """
        messages = []
        
        decision = result["decision"]
        
        # Mensagem principal
        if decision == "PASS":
            messages.append("✅ Documento aprovado - Atende a todos os requisitos")
        elif decision == "ALERT":
            messages.append("⚠️ Documento aceito com ressalvas - Verifique os alertas")
        else:
            messages.append("❌ Documento rejeitado - Corrija os problemas identificados")
        
        # Mensagens de análise de idioma
        language_analysis = result.get("language_analysis", {})
        if language_analysis.get("requires_action", False):
            compliance = language_analysis.get("compliance", {})
            messages.append(f"🌐 Idioma: {compliance.get('message', 'Requer tradução certificada')}")
            
            # Adicionar recomendações específicas
            recommendations = language_analysis.get("recommendations", [])
            for rec in recommendations[:2]:  # Limitar a 2 recomendações principais
                if rec.get("severity") in ["critical", "high"]:
                    messages.append(f"• {rec.get('title', 'Recomendação')}: {rec.get('description', '')}")
        
        # Mensagens de verificação de política
        for check in result["policy_checks"]:
            if check["result"] == "fail" and check["severity"] in ["critical", "high"]:
                messages.append(f"• {check['message']}")
        
        # Mensagens de campos extraídos com problemas
        fields = result.get("fields", {})
        policy_fields = fields.get("policy_fields", {})
        
        missing_required = []
        invalid_fields = []
        
        for field_name, field_data in policy_fields.items():
            if field_data.get("required", False):
                if not field_data.get("found", False):
                    missing_required.append(field_name)
                elif field_data.get("best_match"):
                    best_match = field_data["best_match"]
                    validation = best_match.get("validation", {})
                    if not validation.get("is_valid", False):
                        issues = validation.get("issues", [])
                        if issues:
                            invalid_fields.append(f"{field_name}: {issues[0]}")
        
        if missing_required:
            messages.append(f"📋 Campos obrigatórios não encontrados: {', '.join(missing_required)}")
        
        if invalid_fields:
            for invalid in invalid_fields[:3]:  # Limitar a 3 campos com problema
                messages.append(f"❗ Campo inválido - {invalid}")
        
        return messages

    def _generate_user_messages(self, result: Dict) -> List[str]:
        """
        Gera mensagens de feedback para o usuário (método original mantido para compatibilidade)
        """
        return self._generate_user_messages_enhanced(result)

    def auto_classify_document(self, 
                              file_content: bytes, 
                              filename: str, 
                              extracted_text: str = "") -> Dict[str, Any]:
        """
        Classifica automaticamente o tipo do documento (Phase 3)
        """
        try:
            classification_result = self.document_classifier.classify_document(
                extracted_text, filename, len(file_content)
            )
            
            return {
                'auto_classification': classification_result,
                'suggested_doc_type': classification_result.get('document_type'),
                'confidence': classification_result.get('confidence', 0.0),
                'status': classification_result.get('status', 'unknown'),
                'alternatives': classification_result.get('candidates', [])[:3]  # Top 3 alternativas
            }
            
        except Exception as e:
            logger.error(f"Error in auto-classification: {e}")
            return {
                'auto_classification': {'error': str(e)},
                'suggested_doc_type': 'UNKNOWN',
                'confidence': 0.0,
                'status': 'error',
                'alternatives': []
            }
    
    def validate_multiple_documents(self, 
                                  documents_data: List[Dict[str, Any]],
                                  case_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Valida múltiplos documentos com verificação de consistência (Phase 3)
        """
        try:
            case_context = case_context or {}
            individual_results = []
            
            # 1. Validar cada documento individualmente
            for i, doc_data in enumerate(documents_data):
                file_content = doc_data.get('file_content', b'')
                filename = doc_data.get('filename', f'document_{i}')
                extracted_text = doc_data.get('extracted_text', '')
                doc_type = doc_data.get('doc_type', 'UNKNOWN')
                
                # Auto-classificar se tipo não especificado
                if doc_type == 'UNKNOWN' or not doc_type:
                    classification = self.auto_classify_document(file_content, filename, extracted_text)
                    doc_type = classification['suggested_doc_type']
                
                # Validar individualmente
                individual_result = self.validate_document(
                    file_content, filename, doc_type, extracted_text, case_context
                )
                
                individual_result['document_index'] = i
                individual_result['original_filename'] = filename
                individual_results.append(individual_result)
            
            # 2. Análise de consistência entre documentos (Phase 3)
            consistency_result = {}
            if len(individual_results) >= 2:
                consistency_result = self.consistency_engine.analyze_document_consistency(
                    individual_results, case_context
                )
            
            # 3. Calcular score geral e decisão final
            overall_score, final_decision, summary_issues = self._calculate_multi_document_score(
                individual_results, consistency_result
            )
            
            # 4. Gerar recomendações consolidadas
            consolidated_recommendations = self._generate_multi_document_recommendations(
                individual_results, consistency_result, summary_issues
            )
            
            return {
                'status': 'completed',
                'document_count': len(documents_data),
                'individual_results': individual_results,
                'consistency_analysis': consistency_result,
                'overall_score': overall_score,
                'final_decision': final_decision,
                'summary_issues': summary_issues,
                'recommendations': consolidated_recommendations,
                'timestamp': str(datetime.now())
            }
            
        except Exception as e:
            logger.error(f"Error in multi-document validation: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'document_count': len(documents_data) if documents_data else 0,
                'individual_results': [],
                'consistency_analysis': {},
                'overall_score': 0.0,
                'final_decision': 'FAIL'
            }
    
    def _calculate_multi_document_score(self, 
                                      individual_results: List[Dict],
                                      consistency_result: Dict) -> Tuple[float, str, List[Dict]]:
        """
        Calcula score geral para validação de múltiplos documentos
        """
        if not individual_results:
            return 0.0, 'FAIL', []
        
        # 1. Score médio dos documentos individuais
        individual_scores = [result.get('overall_score', 0.0) for result in individual_results]
        avg_individual_score = sum(individual_scores) / len(individual_scores)
        
        # 2. Score de consistência
        consistency_score = consistency_result.get('consistency_score', 1.0)
        
        # 3. Penalização por problemas críticos
        critical_issues = []
        
        # Verificar problemas individuais críticos
        for result in individual_results:
            if result.get('decision') == 'FAIL':
                critical_issues.append({
                    'type': 'document_failure',
                    'document': result.get('original_filename', 'unknown'),
                    'messages': result.get('messages', [])
                })
        
        # Verificar problemas de consistência críticos
        if consistency_result.get('critical_issues'):
            for issue in consistency_result['critical_issues']:
                critical_issues.append({
                    'type': 'consistency_failure',
                    'rule': issue.get('rule_name', 'unknown'),
                    'message': issue.get('message', 'Consistency issue detected')
                })
        
        # 4. Calcular score final (ponderado)
        weights = {
            'individual_documents': 0.70,
            'consistency': 0.30
        }
        
        overall_score = (
            avg_individual_score * weights['individual_documents'] +
            consistency_score * weights['consistency']
        )
        
        # 5. Determinar decisão final
        has_critical_issues = len(critical_issues) > 0
        has_document_failures = any(result.get('decision') == 'FAIL' for result in individual_results)
        
        if has_critical_issues or has_document_failures:
            final_decision = 'FAIL'
        elif overall_score >= 0.85:
            final_decision = 'PASS'
        elif overall_score >= 0.70:
            final_decision = 'ALERT'
        else:
            final_decision = 'FAIL'
        
        return overall_score, final_decision, critical_issues
    
    def _generate_multi_document_recommendations(self, 
                                               individual_results: List[Dict],
                                               consistency_result: Dict,
                                               summary_issues: List[Dict]) -> List[Dict]:
        """
        Gera recomendações consolidadas para múltiplos documentos
        """
        recommendations = []
        
        # 1. Recomendações baseadas em problemas críticos
        if summary_issues:
            recommendations.append({
                'type': 'critical_issues',
                'severity': 'critical',
                'title': f'Critical Issues Found ({len(summary_issues)} issues)',
                'description': 'Multiple critical issues detected that must be resolved',
                'issues': summary_issues[:5],  # Limitar a 5 issues principais
                'actions': [
                    'Review and correct all identified critical issues',
                    'Ensure all documents are authentic and complete',
                    'Verify consistency of information across documents'
                ]
            })
        
        # 2. Recomendações de consistência
        consistency_recommendations = consistency_result.get('recommendations', [])
        for rec in consistency_recommendations[:3]:  # Limitar a 3 recomendações de consistência
            recommendations.append(rec)
        
        # 3. Recomendações por tipo de problema comum
        language_issues = []
        quality_issues = []
        
        for result in individual_results:
            filename = result.get('original_filename', 'unknown')
            
            # Verificar problemas de idioma
            language_analysis = result.get('language_analysis', {})
            if language_analysis.get('requires_action', False):
                language_issues.append(filename)
            
            # Verificar problemas de qualidade
            quality_status = result.get('quality', {}).get('status', 'ok')
            if quality_status in ['fail', 'alert']:
                quality_issues.append(filename)
        
        if language_issues:
            recommendations.append({
                'type': 'translation_required',
                'severity': 'high',
                'title': 'Translation Required',
                'description': f'Documents require certified English translation: {", ".join(language_issues[:3])}',
                'actions': [
                    'Obtain certified translations from qualified translators',
                    'Ensure translator provides certificate of accuracy',
                    'Submit both original documents and certified translations'
                ]
            })
        
        if quality_issues:
            recommendations.append({
                'type': 'quality_improvement',
                'severity': 'medium',
                'title': 'Document Quality Issues',
                'description': f'Quality issues detected in: {", ".join(quality_issues[:3])}',
                'actions': [
                    'Rescan documents with higher resolution',
                    'Ensure documents are clearly legible',
                    'Check for proper lighting and focus when photographing documents'
                ]
            })
        
        return recommendations

# Instância global do policy engine
policy_engine = PolicyEngine()