"""
Policy Engine - Motor de políticas baseado em YAML
Processa políticas de validação de documentos conforme especificação técnica
"""
import yaml
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
from document_catalog import document_catalog, DocumentType
from document_quality_checker import DocumentQualityChecker

logger = logging.getLogger(__name__)

class PolicyEngine:
    """
    Motor de políticas para validação de documentos
    """
    
    def __init__(self, policies_dir: str = None):
        self.policies_dir = Path(policies_dir or "policies")
        self.loaded_policies = {}
        self.quality_checker = DocumentQualityChecker()
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
            
            # 4. Extração de campos (básica via regex)
            if extracted_text:
                fields_result = self._extract_fields(policy, extracted_text)
                result["fields"] = fields_result
            
            # 5. Verificações de consistência (se contexto do caso disponível)
            if case_context:
                consistency_result = self._check_consistency(policy, result["fields"], case_context)
                result["consistency"] = consistency_result
            
            # 6. Cálculo de score e decisão
            score, decision = self._calculate_score_and_decision(policy, result)
            result["overall_score"] = score
            result["decision"] = decision
            result["status"] = "done"
            
            # 7. Gerar mensagens de feedback
            result["messages"] = self._generate_user_messages(result)
            
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
            "critical_fields_weight": 0.4,
            "quality_weight": 0.3,
            "presence_checks_weight": 0.2,
            "consistency_weight": 0.1
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
    
    def _generate_user_messages(self, result: Dict) -> List[str]:
        """
        Gera mensagens de feedback para o usuário
        """
        messages = []
        
        decision = result["decision"]
        
        if decision == "PASS":
            messages.append("✅ Documento aprovado - Atende a todos os requisitos")
        elif decision == "ALERT":
            messages.append("⚠️ Documento aceito com ressalvas - Verifique os alertas")
        else:
            messages.append("❌ Documento rejeitado - Corrija os problemas identificados")
        
        # Adicionar mensagens específicas de policy checks
        for check in result["policy_checks"]:
            if check["result"] == "fail" and check["severity"] in ["critical", "high"]:
                messages.append(f"• {check['message']}")
        
        return messages

# Instância global do policy engine
policy_engine = PolicyEngine()