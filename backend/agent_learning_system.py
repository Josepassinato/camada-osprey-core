"""
Agent Learning System - Sistema de Aprendizado Contínuo
Os agentes construtores aprendem com cada correção do QA Agent
e evitam repetir os mesmos erros em processos futuros
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class AgentLearningSystem:
    """
    Sistema de aprendizado contínuo para agentes construtores
    Armazena lições aprendidas e padrões de erros para evitar repetição
    """
    
    def __init__(self, db):
        """Inicializa o sistema de aprendizado com conexão MongoDB"""
        self.db = db
        self.collection = db.agent_learning
        
        # Categorias de aprendizado por agente
        self.agent_categories = {
            "document_analyzer": [
                "missing_documents",
                "invalid_format",
                "quality_issues",
                "validation_failures"
            ],
            "form_filler": [
                "missing_fields",
                "invalid_formats",
                "data_inconsistencies",
                "validation_errors"
            ],
            "translation_agent": [
                "spelling_errors",
                "grammar_mistakes",
                "formatting_issues",
                "terminology_errors"
            ],
            "specialized_agent": [
                "uscis_criteria_failures",
                "compliance_issues",
                "evidence_insufficiency",
                "critical_missing_items"
            ]
        }
        
        logger.info("✅ Agent Learning System inicializado")
    
    async def record_lesson(
        self,
        agent_name: str,
        case_id: str,
        problem: Dict[str, Any],
        correction: Dict[str, Any],
        success: bool
    ):
        """
        Registra uma lição aprendida por um agente
        
        Args:
            agent_name: Nome do agente (document_analyzer, form_filler, etc)
            case_id: ID do caso onde ocorreu
            problem: Detalhes do problema identificado pelo QA
            correction: Ação de correção tomada
            success: Se a correção foi bem-sucedida
        """
        lesson = {
            "agent_name": agent_name,
            "case_id": case_id,
            "timestamp": datetime.utcnow(),
            "problem": {
                "type": problem.get('type'),
                "description": problem.get('description'),
                "severity": problem.get('severity'),
                "category": problem.get('category')
            },
            "correction": {
                "action": correction.get('action'),
                "details": correction.get('details'),
                "status": correction.get('status')
            },
            "success": success,
            "form_code": problem.get('form_code'),  # Tipo de visto
            "pattern_detected": self._detect_pattern(problem),
            "confidence_score": self._calculate_confidence(problem, correction, success)
        }
        
        # Salvar no MongoDB
        await self.collection.insert_one(lesson)
        
        logger.info(
            f"📚 Lição registrada: {agent_name} - {problem.get('type')} "
            f"(Success: {success})"
        )
        
        return lesson
    
    async def get_relevant_lessons(
        self,
        agent_name: str,
        problem_type: str,
        form_code: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca lições relevantes para um problema atual
        
        Args:
            agent_name: Nome do agente
            problem_type: Tipo do problema
            form_code: Tipo de visto (opcional)
            limit: Número máximo de lições
            
        Returns:
            Lista de lições aprendidas relevantes
        """
        query = {
            "agent_name": agent_name,
            "problem.type": problem_type,
            "success": True  # Apenas lições bem-sucedidas
        }
        
        if form_code:
            query["form_code"] = form_code
        
        # Buscar lições ordenadas por data (mais recentes primeiro)
        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        lessons = await cursor.to_list(length=limit)
        
        logger.info(
            f"🔍 Encontradas {len(lessons)} lições para {agent_name} - {problem_type}"
        )
        
        return lessons
    
    async def get_preventive_recommendations(
        self,
        agent_name: str,
        form_code: str,
        case_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Obtém recomendações preventivas baseadas em lições aprendidas
        
        Args:
            agent_name: Nome do agente
            form_code: Tipo de visto
            case_data: Dados atuais do caso
            
        Returns:
            Lista de recomendações preventivas
        """
        # Buscar problemas comuns para este tipo de visto
        common_problems = await self._get_common_problems(agent_name, form_code)
        
        recommendations = []
        
        for problem in common_problems:
            # Verificar se o caso atual pode ter este problema
            risk_score = self._assess_risk(problem, case_data)
            
            if risk_score > 0.5:  # 50% de probabilidade
                # Buscar melhor correção conhecida
                best_correction = await self._get_best_correction(
                    agent_name, 
                    problem['problem_type']
                )
                
                recommendations.append({
                    "problem_type": problem['problem_type'],
                    "description": problem['description'],
                    "risk_score": risk_score,
                    "occurrence_count": problem['count'],
                    "recommended_action": best_correction,
                    "priority": "high" if risk_score > 0.7 else "medium"
                })
        
        # Ordenar por risk_score
        recommendations.sort(key=lambda x: x['risk_score'], reverse=True)
        
        logger.info(
            f"💡 {len(recommendations)} recomendações preventivas para {agent_name} - {form_code}"
        )
        
        return recommendations
    
    async def _get_common_problems(
        self,
        agent_name: str,
        form_code: str,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """Obtém problemas mais comuns para um agente e tipo de visto"""
        pipeline = [
            {
                "$match": {
                    "agent_name": agent_name,
                    "form_code": form_code
                }
            },
            {
                "$group": {
                    "_id": {
                        "problem_type": "$problem.type",
                        "description": "$problem.description"
                    },
                    "count": {"$sum": 1},
                    "success_rate": {
                        "$avg": {"$cond": ["$success", 1, 0]}
                    }
                }
            },
            {
                "$match": {
                    "count": {"$gte": min_occurrences}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 10
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        problems = await cursor.to_list(length=10)
        
        # Formatar resultado
        return [
            {
                "problem_type": p['_id']['problem_type'],
                "description": p['_id']['description'],
                "count": p['count'],
                "success_rate": p['success_rate']
            }
            for p in problems
        ]
    
    async def _get_best_correction(
        self,
        agent_name: str,
        problem_type: str
    ) -> Dict[str, Any]:
        """Obtém a melhor correção conhecida para um tipo de problema"""
        # Buscar correções bem-sucedidas
        query = {
            "agent_name": agent_name,
            "problem.type": problem_type,
            "success": True
        }
        
        # Ordenar por confidence_score
        cursor = self.collection.find(query).sort("confidence_score", -1).limit(1)
        lessons = await cursor.to_list(length=1)
        
        if lessons:
            return {
                "action": lessons[0]['correction']['action'],
                "details": lessons[0]['correction']['details'],
                "confidence": lessons[0]['confidence_score']
            }
        
        return {
            "action": "manual_review",
            "details": "No successful correction pattern found",
            "confidence": 0.0
        }
    
    def _detect_pattern(self, problem: Dict[str, Any]) -> str:
        """Detecta padrão do problema para facilitar busca futura"""
        desc = problem.get('description', '').lower()
        
        # Padrões comuns
        if 'missing' in desc:
            if 'document' in desc:
                return "missing_document"
            elif 'field' in desc:
                return "missing_field"
            else:
                return "missing_data"
        
        elif 'invalid' in desc or 'incorrect' in desc:
            if 'format' in desc:
                return "invalid_format"
            elif 'email' in desc:
                return "invalid_email"
            elif 'phone' in desc:
                return "invalid_phone"
            else:
                return "invalid_data"
        
        elif 'error' in desc:
            if 'spelling' in desc or 'typo' in desc:
                return "spelling_error"
            elif 'grammar' in desc:
                return "grammar_error"
            else:
                return "general_error"
        
        else:
            return "other"
    
    def _calculate_confidence(
        self,
        problem: Dict[str, Any],
        correction: Dict[str, Any],
        success: bool
    ) -> float:
        """Calcula score de confiança da lição"""
        base_score = 0.5
        
        # Aumentar se foi bem-sucedido
        if success:
            base_score += 0.3
        
        # Aumentar se tem detalhes completos
        if correction.get('details'):
            base_score += 0.1
        
        # Aumentar se problema é crítico (mostra importância)
        if problem.get('severity') == 'critical':
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _assess_risk(
        self,
        problem: Dict[str, Any],
        case_data: Dict[str, Any]
    ) -> float:
        """Avalia risco de um problema ocorrer no caso atual"""
        risk_score = 0.0
        
        problem_type = problem['problem_type']
        
        # Verificar dados do caso para calcular risco
        basic_data = case_data.get('basic_data', {})
        form_responses = case_data.get('simplified_form_responses', {})
        documents = case_data.get('documents', [])
        
        # Risco de missing_field
        if 'missing' in problem_type and 'field' in problem_type:
            required_fields = ['full_name', 'email', 'phone', 'date_of_birth']
            missing_count = sum(1 for field in required_fields if not basic_data.get(field))
            risk_score = missing_count / len(required_fields)
        
        # Risco de missing_document
        elif 'missing' in problem_type and 'document' in problem_type:
            min_docs = 3
            if len(documents) < min_docs:
                risk_score = 1.0 - (len(documents) / min_docs)
        
        # Risco de invalid_format
        elif 'invalid' in problem_type and 'format' in problem_type:
            # Verificar formatos de email, phone, etc
            if basic_data.get('email') and '@' not in basic_data['email']:
                risk_score = 0.8
            elif basic_data.get('passport_number') and len(basic_data['passport_number']) < 6:
                risk_score = 0.7
        
        # Usar taxa de ocorrência como base
        else:
            occurrence_rate = problem['count'] / 100  # Normalizar
            risk_score = min(0.6, occurrence_rate)
        
        return risk_score
    
    async def get_learning_statistics(
        self,
        agent_name: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas de aprendizado
        
        Args:
            agent_name: Nome do agente (ou None para todos)
            days: Período em dias
            
        Returns:
            Estatísticas de aprendizado
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = {"timestamp": {"$gte": start_date}}
        if agent_name:
            query["agent_name"] = agent_name
        
        # Total de lições
        total_lessons = await self.collection.count_documents(query)
        
        # Lições bem-sucedidas
        success_query = {**query, "success": True}
        successful_lessons = await self.collection.count_documents(success_query)
        
        # Taxa de sucesso
        success_rate = (successful_lessons / total_lessons) if total_lessons > 0 else 0
        
        # Problemas mais comuns
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$problem.type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        top_problems = await cursor.to_list(length=5)
        
        # Agentes mais ativos
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$agent_name",
                    "lesson_count": {"$sum": 1},
                    "success_count": {
                        "$sum": {"$cond": ["$success", 1, 0]}
                    }
                }
            },
            {"$sort": {"lesson_count": -1}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        agent_stats = await cursor.to_list(length=10)
        
        return {
            "period_days": days,
            "total_lessons": total_lessons,
            "successful_lessons": successful_lessons,
            "success_rate": success_rate,
            "top_problems": [
                {
                    "problem_type": p['_id'],
                    "occurrences": p['count']
                }
                for p in top_problems
            ],
            "agent_performance": [
                {
                    "agent": a['_id'],
                    "lessons": a['lesson_count'],
                    "successes": a['success_count'],
                    "success_rate": a['success_count'] / a['lesson_count']
                }
                for a in agent_stats
            ]
        }
    
    async def apply_learned_corrections(
        self,
        agent_name: str,
        case_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Aplica correções aprendidas proativamente
        
        Args:
            agent_name: Nome do agente
            case_data: Dados do caso
            
        Returns:
            Lista de correções aplicadas
        """
        form_code = case_data.get('form_code')
        
        # Obter recomendações preventivas
        recommendations = await self.get_preventive_recommendations(
            agent_name,
            form_code,
            case_data
        )
        
        corrections_applied = []
        
        for rec in recommendations:
            if rec['priority'] == 'high' and rec['risk_score'] > 0.7:
                # Aplicar correção preventiva
                logger.info(
                    f"🔧 Aplicando correção preventiva: {rec['problem_type']}"
                )
                
                # Simular aplicação (em implementação real, chamar agente)
                correction = {
                    "problem_type": rec['problem_type'],
                    "action_taken": rec['recommended_action']['action'],
                    "status": "applied_preventively",
                    "confidence": rec['recommended_action']['confidence']
                }
                
                corrections_applied.append(correction)
        
        logger.info(
            f"✅ {len(corrections_applied)} correções preventivas aplicadas"
        )
        
        return corrections_applied


# Singleton instance
_learning_system = None

async def get_learning_system(db):
    """Retorna instância singleton do Learning System"""
    global _learning_system
    if _learning_system is None:
        _learning_system = AgentLearningSystem(db)
    return _learning_system
