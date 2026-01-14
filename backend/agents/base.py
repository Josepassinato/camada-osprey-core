"""
Base Agent Class

Abstract base class for all AI agents in the Osprey platform.
Provides common functionality for LLM interactions, logging, and metrics.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from backend.llm.portkey_client import LLMClient
from backend.llm.types import ChatMessage, MessageRole, LLMResponse
from backend.llm.exceptions import (
    LLMException,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMCircuitBreakerError,
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents
    
    Provides:
    - Unified LLM client interface
    - Error handling and retry logic
    - Logging and metrics collection
    - Common helper methods
    
    All agents should inherit from this class and implement the `process()` method.
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        agent_name: str = "base_agent",
        default_model: str = "gpt-4o",
        default_temperature: float = 0.7,
        enable_metrics: bool = True,
    ):
        """
        Initialize base agent
        
        Args:
            llm_client: LLM client instance (creates new one if not provided)
            agent_name: Unique identifier for this agent
            default_model: Default model to use for LLM calls
            default_temperature: Default temperature for LLM calls
            enable_metrics: Whether to collect metrics
        """
        self.llm_client = llm_client or LLMClient()
        self.agent_name = agent_name
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.enable_metrics = enable_metrics
        
        # Metrics
        self._metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_latency_ms": 0,
            "errors": {},
        }
        
        logger.info(f"Initialized {self.agent_name} agent")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return result
        
        This method must be implemented by all subclasses.
        
        Args:
            input_data: Input data for the agent to process
        
        Returns:
            Dict containing the processing result
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement process() method"
        )
    
    async def _call_llm(
        self,
        messages: List[Union[Dict[str, str], ChatMessage]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        prompt_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Helper method for LLM calls with error handling and metrics
        
        Args:
            messages: List of chat messages
            model: Model to use (defaults to agent's default_model)
            temperature: Temperature (defaults to agent's default_temperature)
            max_tokens: Maximum tokens to generate
            prompt_id: Portkey prompt ID (if using prompt templates)
            **kwargs: Additional parameters for LLM call
        
        Returns:
            String content from LLM response
        
        Raises:
            LLMException: If LLM call fails after retries
        """
        start_time = time.time()
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        
        try:
            logger.debug(
                f"[{self.agent_name}] Calling LLM with model={model}, "
                f"temperature={temperature}, messages={len(messages)}"
            )
            
            # Use prompt template if prompt_id provided
            if prompt_id:
                response = await self.llm_client.completion_with_prompt(
                    prompt_id=prompt_id,
                    variables=kwargs.get("variables", {}),
                    model=model,
                    **kwargs
                )
            else:
                response = await self.llm_client.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(
                success=True,
                tokens=response.usage.total_tokens,
                latency_ms=latency_ms
            )
            
            logger.info(
                f"[{self.agent_name}] LLM call successful: "
                f"model={response.model}, tokens={response.usage.total_tokens}, "
                f"latency={latency_ms:.2f}ms"
            )
            
            return response.content
            
        except LLMRateLimitError as e:
            logger.warning(
                f"[{self.agent_name}] Rate limit exceeded: {e}",
                extra={"retry_after": e.retry_after}
            )
            self._update_metrics(success=False, error_type="rate_limit")
            raise
            
        except LLMTimeoutError as e:
            logger.error(
                f"[{self.agent_name}] LLM call timed out: {e}",
                extra={"timeout_seconds": e.timeout_seconds}
            )
            self._update_metrics(success=False, error_type="timeout")
            raise
            
        except LLMCircuitBreakerError as e:
            logger.error(
                f"[{self.agent_name}] Circuit breaker open: {e}",
                extra={
                    "provider": e.provider,
                    "failure_count": e.failure_count,
                    "threshold": e.threshold
                }
            )
            self._update_metrics(success=False, error_type="circuit_breaker")
            raise
            
        except LLMProviderError as e:
            logger.error(
                f"[{self.agent_name}] Provider error: {e}",
                extra={
                    "provider": e.provider,
                    "model": e.model,
                    "details": e.details
                }
            )
            self._update_metrics(success=False, error_type="provider_error")
            raise
            
        except LLMException as e:
            logger.error(
                f"[{self.agent_name}] LLM error: {e}",
                extra={"details": e.details}
            )
            self._update_metrics(success=False, error_type="llm_error")
            raise
            
        except Exception as e:
            logger.error(
                f"[{self.agent_name}] Unexpected error in LLM call: {e}",
                exc_info=True
            )
            self._update_metrics(success=False, error_type="unexpected")
            raise LLMException(
                f"Unexpected error in {self.agent_name}: {str(e)}",
                details={"agent": self.agent_name, "error": str(e)}
            )
    
    async def _call_llm_with_response(
        self,
        messages: List[Union[Dict[str, str], ChatMessage]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Helper method for LLM calls that returns full response object
        
        Similar to _call_llm but returns the complete LLMResponse
        instead of just the content string.
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse object with content, usage, and metadata
        
        Raises:
            LLMException: If LLM call fails
        """
        start_time = time.time()
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        
        try:
            response = await self.llm_client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(
                success=True,
                tokens=response.usage.total_tokens,
                latency_ms=latency_ms
            )
            
            return response
            
        except Exception as e:
            self._update_metrics(success=False, error_type=type(e).__name__)
            raise
    
    def _build_messages(
        self,
        system_prompt: Optional[str] = None,
        user_message: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[ChatMessage]:
        """
        Helper to build message list for LLM calls
        
        Args:
            system_prompt: System prompt (optional)
            user_message: User message (optional)
            conversation_history: Previous messages (optional)
        
        Returns:
            List of ChatMessage objects
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append(
                ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
            )
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                role = MessageRole(msg.get("role", "user"))
                content = msg.get("content", "")
                messages.append(ChatMessage(role=role, content=content))
        
        # Add current user message
        if user_message:
            messages.append(
                ChatMessage(role=MessageRole.USER, content=user_message)
            )
        
        return messages
    
    def _update_metrics(
        self,
        success: bool,
        tokens: int = 0,
        latency_ms: float = 0,
        error_type: Optional[str] = None
    ) -> None:
        """
        Update agent metrics
        
        Args:
            success: Whether the call was successful
            tokens: Number of tokens used
            latency_ms: Latency in milliseconds
            error_type: Type of error if failed
        """
        if not self.enable_metrics:
            return
        
        self._metrics["total_calls"] += 1
        
        if success:
            self._metrics["successful_calls"] += 1
            self._metrics["total_tokens"] += tokens
            self._metrics["total_latency_ms"] += latency_ms
        else:
            self._metrics["failed_calls"] += 1
            if error_type:
                self._metrics["errors"][error_type] = (
                    self._metrics["errors"].get(error_type, 0) + 1
                )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent metrics
        
        Returns:
            Dict containing agent metrics including:
            - total_calls: Total number of LLM calls
            - successful_calls: Number of successful calls
            - failed_calls: Number of failed calls
            - success_rate: Percentage of successful calls
            - total_tokens: Total tokens used
            - avg_tokens_per_call: Average tokens per successful call
            - total_latency_ms: Total latency in milliseconds
            - avg_latency_ms: Average latency per successful call
            - errors: Breakdown of errors by type
        """
        metrics = self._metrics.copy()
        
        # Calculate derived metrics
        if metrics["total_calls"] > 0:
            metrics["success_rate"] = (
                metrics["successful_calls"] / metrics["total_calls"] * 100
            )
        else:
            metrics["success_rate"] = 0.0
        
        if metrics["successful_calls"] > 0:
            metrics["avg_tokens_per_call"] = (
                metrics["total_tokens"] / metrics["successful_calls"]
            )
            metrics["avg_latency_ms"] = (
                metrics["total_latency_ms"] / metrics["successful_calls"]
            )
        else:
            metrics["avg_tokens_per_call"] = 0.0
            metrics["avg_latency_ms"] = 0.0
        
        return metrics
    
    def reset_metrics(self) -> None:
        """Reset agent metrics to zero"""
        self._metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_latency_ms": 0,
            "errors": {},
        }
        logger.info(f"[{self.agent_name}] Metrics reset")
    
    def __repr__(self) -> str:
        """String representation of agent"""
        return (
            f"{self.__class__.__name__}("
            f"name={self.agent_name}, "
            f"model={self.default_model}, "
            f"calls={self._metrics['total_calls']}"
            f")"
        )
