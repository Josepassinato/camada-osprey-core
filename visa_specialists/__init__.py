"""
Visa Specialists - Multi-Agent Architecture
Cada agente é especializado em um tipo específico de visto
"""

from .supervisor.supervisor_agent import SupervisorAgent
from .b2_extension.b2_agent import B2ExtensionAgent
from .h1b_worker.h1b_agent import H1BWorkerAgent

__all__ = ['SupervisorAgent', 'B2ExtensionAgent', 'H1BWorkerAgent']
