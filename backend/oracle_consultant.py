"""
DEPRECATED: This module has been moved to backend/agents/oracle/

This compatibility shim will be removed in a future version.
Please update your imports to:
    from agents.oracle import ImmigrationOracle, consult_oracle, oracle
"""

import warnings

warnings.warn(
    "oracle_consultant module is deprecated. "
    "Use 'from agents.oracle import ImmigrationOracle, consult_oracle, oracle' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location for backward compatibility
from agents.oracle import ImmigrationOracle, consult_oracle, oracle

__all__ = ["ImmigrationOracle", "consult_oracle", "oracle"]
