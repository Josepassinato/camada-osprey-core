"""
Knowledge Management Package

This package handles knowledge base management for internal agents,
including document storage, retrieval, and helper utilities for AI agents.
"""

from .helper import AgentKnowledgeHelper, get_knowledge_helper
from .manager import (
    KNOWLEDGE_BASE_CATEGORIES,
    SUPPORTED_FORM_TYPES,
    KnowledgeBaseManager,
)

__all__ = [
    "KnowledgeBaseManager",
    "KNOWLEDGE_BASE_CATEGORIES",
    "SUPPORTED_FORM_TYPES",
    "AgentKnowledgeHelper",
    "get_knowledge_helper",
]
