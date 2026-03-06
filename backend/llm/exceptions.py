"""
LLM Exception Classes

Custom exceptions for LLM operations with detailed error information.
"""

from typing import Any, Dict, Optional


class LLMException(Exception):
    """Base exception for all LLM operations"""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.provider = provider
        self.model = model
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.model:
            parts.append(f"Model: {self.model}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


class LLMProviderError(LLMException):
    """
    Provider-specific error (OpenAI, Anthropic, Google, etc.)

    Raised when the LLM provider returns an error response.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        details = details or {}
        if status_code:
            details["status_code"] = status_code
        if error_code:
            details["error_code"] = error_code
        super().__init__(message, provider, model, details)


class LLMRateLimitError(LLMException):
    """
    Rate limit exceeded

    Raised when the provider's rate limit is exceeded.
    Includes retry_after information when available.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        model: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.retry_after = retry_after
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, provider, model, details)


class LLMCostLimitError(LLMException):
    """
    Cost budget exceeded

    Raised when the configured cost budget is exceeded.
    """

    def __init__(
        self,
        message: str,
        current_cost: float,
        budget_limit: float,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.current_cost = current_cost
        self.budget_limit = budget_limit
        details = details or {}
        details.update(
            {
                "current_cost": current_cost,
                "budget_limit": budget_limit,
                "exceeded_by": current_cost - budget_limit,
            }
        )
        super().__init__(message, provider, model, details)


class LLMTimeoutError(LLMException):
    """
    Request timeout

    Raised when an LLM request exceeds the configured timeout.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.timeout_seconds = timeout_seconds
        details = details or {}
        details["timeout_seconds"] = timeout_seconds
        super().__init__(message, provider, model, details)


class PromptNotFoundError(LLMException):
    """
    Portkey prompt ID not found

    Raised when a referenced Portkey prompt template cannot be found.
    """

    def __init__(self, message: str, prompt_id: str, details: Optional[Dict[str, Any]] = None):
        self.prompt_id = prompt_id
        details = details or {}
        details["prompt_id"] = prompt_id
        super().__init__(message, provider="portkey", details=details)


class LLMValidationError(LLMException):
    """
    Input validation error

    Raised when request parameters fail validation.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.field = field
        self.value = value
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details=details)


class LLMCircuitBreakerError(LLMException):
    """
    Circuit breaker open

    Raised when the circuit breaker is open due to repeated failures.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        failure_count: int,
        threshold: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.failure_count = failure_count
        self.threshold = threshold
        details = details or {}
        details.update({"failure_count": failure_count, "threshold": threshold})
        super().__init__(message, provider=provider, details=details)


class LLMContentFilterError(LLMException):
    """
    Content filtered by provider

    Raised when the provider's content filter blocks the request or response.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        model: Optional[str] = None,
        filter_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.filter_type = filter_type
        details = details or {}
        if filter_type:
            details["filter_type"] = filter_type
        super().__init__(message, provider, model, details)
