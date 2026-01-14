"""
Specialized Agent Coordinator

Coordinates multiple specialized agents for comprehensive analysis.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

from .compliance_checker import ComplianceCheckAgent
from .document_validator import DocumentValidationAgent
from .eligibility_analyst import EligibilityAnalysisAgent
from .form_validator import FormValidationAgent
from .letter_writer import ImmigrationLetterWriterAgent
from .translator import USCISFormTranslatorAgent
from .triage import UrgencyTriageAgent

logger = logging.getLogger(__name__)


class SpecializedAgentCoordinator:
    """
    Coordinates multiple specialized agents for comprehensive analysis

    Capabilities:
    - Multi-agent orchestration
    - Task routing and delegation
    - Result aggregation
    - Workflow management
    """

    def __init__(self, llm_client: Optional[LLMClient] = None, db=None):
        """
        Initialize coordinator with all specialized agents

        Args:
            llm_client: Shared LLM client for all agents
            db: MongoDB connection for knowledge base access
        """
        self.llm_client = llm_client or LLMClient()
        self.db = db

        # Initialize all specialized agents
        self.agents = {
            "document_validator": DocumentValidationAgent(llm_client=self.llm_client, db=self.db),
            "form_validator": FormValidationAgent(llm_client=self.llm_client, db=self.db),
            "eligibility_analyst": EligibilityAnalysisAgent(llm_client=self.llm_client, db=self.db),
            "compliance_checker": ComplianceCheckAgent(llm_client=self.llm_client, db=self.db),
            "letter_writer": ImmigrationLetterWriterAgent(llm_client=self.llm_client, db=self.db),
            "uscis_translator": USCISFormTranslatorAgent(llm_client=self.llm_client, db=self.db),
            "triage": UrgencyTriageAgent(llm_client=self.llm_client, db=self.db),
        }

        logger.info("Initialized SpecializedAgentCoordinator with all agents")

    async def analyze_comprehensive(
        self, task_type: str, data: Dict[str, Any], user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using appropriate specialized agents

        Args:
            task_type: Type of task (document_validation, form_validation, etc.)
            data: Task data
            user_context: Optional user context

        Returns:
            Dict containing comprehensive analysis results
        """
        results = {
            "coordinator": "Specialized Agent System",
            "task_type": task_type,
            "analyses": {},
            "summary": {},
            "recommendations": [],
        }

        try:
            # First, use triage to determine which agents to use
            triage_result = await self.agents["triage"].process(
                {
                    "issue_description": f"Task type: {task_type}, Data: {str(data)[:200]}",
                    "context": user_context or {},
                }
            )

            results["triage"] = triage_result

            # Based on task type, call appropriate agents
            if task_type == "document_validation":
                doc_analysis = await self.agents["document_validator"].process(
                    {
                        "document_data": data.get("document_data"),
                        "document_type": data.get("document_type"),
                        "case_context": user_context,
                    }
                )
                results["analyses"]["document_validation"] = doc_analysis

            elif task_type == "form_validation":
                form_analysis = await self.agents["form_validator"].process(
                    {
                        "form_data": data.get("form_data"),
                        "form_type": data.get("form_type"),
                        "visa_type": data.get("visa_type"),
                    }
                )
                results["analyses"]["form_validation"] = form_analysis

            elif task_type == "eligibility_check":
                eligibility_analysis = await self.agents["eligibility_analyst"].process(
                    {
                        "candidate_data": data.get("candidate_data"),
                        "visa_type": data.get("visa_type"),
                    }
                )
                results["analyses"]["eligibility"] = eligibility_analysis

            elif task_type == "compliance_review":
                compliance_analysis = await self.agents["compliance_checker"].process(
                    {
                        "application_data": data.get("application_data"),
                        "visa_type": data.get("visa_type"),
                    }
                )
                results["analyses"]["compliance"] = compliance_analysis

            elif task_type == "letter_writing":
                letter_result = await self.agents["letter_writer"].process(
                    {
                        "letter_type": data.get("letter_type"),
                        "client_facts": data.get("client_facts"),
                        "visa_type": data.get("visa_type"),
                    }
                )
                results["analyses"]["letter_writing"] = letter_result

            elif task_type == "form_translation":
                translation_result = await self.agents["uscis_translator"].process(
                    {
                        "friendly_form_data": data.get("friendly_form_data"),
                        "target_uscis_form": data.get("target_uscis_form"),
                    }
                )
                results["analyses"]["form_translation"] = translation_result

            # Generate summary
            results["summary"] = self._generate_summary(results["analyses"])

            return results

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}", exc_info=True)
            return {
                "coordinator": "Specialized Agent System",
                "error": str(e),
                "analyses": {},
                "summary": {"status": "error"},
                "recommendations": ["Erro no sistema - tente novamente"],
            }

    async def route_to_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request directly to a specific agent

        Args:
            agent_name: Name of the agent to route to
            input_data: Input data for the agent

        Returns:
            Dict containing agent's response
        """
        if agent_name not in self.agents:
            return {
                "error": f"Unknown agent: {agent_name}",
                "available_agents": list(self.agents.keys()),
            }

        try:
            agent = self.agents[agent_name]
            result = await agent.process(input_data)
            return result
        except Exception as e:
            logger.error(f"Error routing to {agent_name}: {e}", exc_info=True)
            return {"error": f"Error in {agent_name}: {str(e)}", "agent": agent_name}

    def get_agent_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from all agents

        Returns:
            Dict containing metrics for each agent
        """
        metrics = {}
        for agent_name, agent in self.agents.items():
            if isinstance(agent, BaseAgent):
                metrics[agent_name] = agent.get_metrics()
        return metrics

    def _generate_summary(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary from multiple analyses

        Args:
            analyses: Dict of analysis results from different agents

        Returns:
            Dict containing summary
        """
        summary = {
            "total_analyses": len(analyses),
            "status": "completed",
            "issues_found": [],
            "recommendations": [],
        }

        # Aggregate issues and recommendations from all analyses
        for analysis_type, analysis_result in analyses.items():
            if isinstance(analysis_result, dict):
                # Collect issues
                if "issues" in analysis_result:
                    issues = analysis_result["issues"]
                    if isinstance(issues, list):
                        summary["issues_found"].extend(issues)

                # Collect recommendations
                if "recommendations" in analysis_result:
                    recs = analysis_result["recommendations"]
                    if isinstance(recs, list):
                        summary["recommendations"].extend(recs)

        return summary


# Factory function
def create_specialized_agent_coordinator(
    llm_client: Optional[LLMClient] = None, db=None
) -> SpecializedAgentCoordinator:
    """Create a SpecializedAgentCoordinator instance"""
    return SpecializedAgentCoordinator(llm_client=llm_client, db=db)
