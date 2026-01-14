"""
Knowledge Management Package

This package handles knowledge base management for internal agents,
including document storage, retrieval, and helper utilities for AI agents.
"""

from .manager import (
    KnowledgeBaseManager,
    KNOWLEDGE_BASE_CATEGORIES,
    SUPPORTED_FORM_TYPES
)
from .helper import AgentKnowledgeHelper, get_knowledge_helper

__all__ = [
    "KnowledgeBaseManager",
    "KNOWLEDGE_BASE_CATEGORIES",
    "SUPPORTED_FORM_TYPES",
    "AgentKnowledgeHelper",
    "get_knowledge_helper",
]
