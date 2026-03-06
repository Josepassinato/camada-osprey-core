"""
Oracle Agent Package

Immigration legal consultant that queries the knowledge base for:
- Form requirements and documentation
- Processing times
- Document validation checklists
"""

from .consultant import ImmigrationOracle, consult_oracle, oracle

__all__ = [
    "ImmigrationOracle",
    "consult_oracle",
    "oracle",
]
