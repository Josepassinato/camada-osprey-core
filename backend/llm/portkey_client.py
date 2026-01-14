"""
Portkey LLM Client

Unified LLM client with Portkey integration for observability, cost tracking,
and multi-provider routing.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Union

try:
    from portkey_ai import Portkey
    PORTKEY_AVAILABLE = True
except ImportError:
    PORTKEY_AVAILABLE = False
    logging.warning("portkey-ai not installed. LLM client will not function.")

from .exceptions import (
    LLMCircuitBreakerError,
    LLMException,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    PromptNotFoundError,
)
from .types import (
    ChatMessage,
    LLMResponse,
    LLMUsage,
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker for failing providers
    
    Prevents cascading failures by temporarily disabling providers
    that are experiencing repeated errors.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_attempts: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_attempts = half_open_attempts
        
        self._failure_count: Dict[str, int] = {}
        self._last_failure_time: Dict[str, datetime] = {}
        self._state: Dict[str, str] = {}  # "closed", "open", "half_open"
        self._half_open_count: Dict[str, int] = {}
    
    def record_success(self, provider: str) -> None:
        """Record successful call"""
        self._failure_count[provider] = 0
        self._state[provider] = "closed"
        self._half_open_count[provider] = 0
    
    def record_failure(self, provider: str) -> None:
        """Record failed call"""
        self._failure_count[provider] = self._failure_count.get(provider, 0) + 1
        self._last_failure_time[provider] = datetime.now()
        
        if self._failure_count[provider] >= self.failure_threshold:
            self._state[provider] = "open"
            logger.warning(
                f"Circuit breaker opened for provider {provider} "
                f"after {self._failure_count[provider]} failures"
            )
    
    def can_attempt(self, provider: str) -> bool:
        """Check if provider can be attempted"""
        state = self._state.get(provider, "closed")
        
        if state == "closed":
            return True
        
        if state == "open":
            # Check if timeout has elapsed
            last_failure = self._last_failure_time.get(provider)
            if last_failure:
                elapsed = (datetime.now() - last_failure).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self._state[provider] = "half_open"
                    self._half_open_count[provider] = 0
                    logger.info(f"Circuit breaker entering half-open state for {provider}")
                    return True
            return False
        
        if state == "half_open":
            # Allow limited attempts in half-open state
            count = self._half_open_count.get(provider, 0)
            if count < self.half_open_attempts:
                self._half_open_count[provider] = count + 1
                return True
            return False
        
        return False
    
    def get_state(self, provider: str) -> str:
        """Get current circuit breaker state"""
        return self._state.get(provider, "closed")


class LLMClient:
    """
    Unified LLM client with Portkey integration
    
    Provides a consistent interface for LLM operations with:
    - Multi-provider routing
    - Automatic retries with exponential backoff
    - Circuit breaker for failing providers
    - Cost tracking and budget limits
    - Observability through Portkey dashboard
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        virtual_key: Optional[str] = None,
        config: Optional[Union[str, Dict[str, Any]]] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        enable_circuit_breaker: bool = True,
    ):
        """
        Initialize LLM client
        
        Args:
            api_key: Portkey API key (defaults to PORTKEY_API_KEY env var)
            virtual_key: Portkey virtual key for provider routing
            config: Portkey config ID or dict for routing rules
            base_url: Custom Portkey gateway URL
            max_retries: Maximum retry attempts for failed requests
            timeout: Request timeout in seconds
            enable_circuit_breaker: Enable circuit breaker for failing providers
        """
        if not PORTKEY_AVAILABLE:
            raise ImportError(
                "portkey-ai package not installed. "
                "Install with: pip install portkey-ai"
            )
        
        self.api_key = api_key or os.getenv("PORTKEY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Portkey API key required. Set PORTKEY_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.virtual_key = virtual_key or os.getenv("PORTKEY_VIRTUAL_KEY")
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Initialize Portkey client
        portkey_kwargs = {
            "api_key": self.api_key,
        }
        
        if self.virtual_key:
            portkey_kwargs["virtual_key"] = self.virtual_key
        
        if config:
            portkey_kwargs["config"] = config
        
        if base_url:
            portkey_kwargs["base_url"] = base_url
        
        self.portkey = Portkey(**portkey_kwargs)
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker() if enable_circuit_breaker else None
        
        # Metrics
        self._total_requests = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        
        logger.info("LLMClient initialized with Portkey integration")
    
    async def chat_completion(
        self,
        messages: List[Union[Dict[str, str], ChatMessage]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute chat completion with Portkey routing
        
        Args:
            messages: List of chat messages
            model: Model identifier (e.g., "gpt-4o", "claude-3-opus")
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stop: Stop sequences
            metadata: Additional metadata for tracking
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with content, usage, and metadata
        
        Raises:
            LLMProviderError: Provider returned an error
            LLMRateLimitError: Rate limit exceeded
            LLMTimeoutError: Request timed out
            LLMCircuitBreakerError: Circuit breaker is open
        """
        # Convert ChatMessage objects to dicts
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted_messages.append(msg.dict(exclude_none=True))
            else:
                formatted_messages.append(msg)
        
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_attempt(model):
            raise LLMCircuitBreakerError(
                f"Circuit breaker open for model {model}",
                provider=model.split("-")[0] if "-" in model else "unknown",
                failure_count=self.circuit_breaker._failure_count.get(model, 0),
                threshold=self.circuit_breaker.failure_threshold
            )
        
        # Build request parameters
        request_params = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            request_params["max_tokens"] = max_tokens
        if top_p is not None:
            request_params["top_p"] = top_p
        if frequency_penalty is not None:
            request_params["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            request_params["presence_penalty"] = presence_penalty
        if stop is not None:
            request_params["stop"] = stop
        
        # Add metadata
        if metadata:
            request_params["metadata"] = metadata
        
        # Add any additional kwargs
        request_params.update(kwargs)
        
        # Execute with retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"LLM request attempt {attempt + 1}/{self.max_retries} "
                    f"to model {model}"
                )
                
                response = await asyncio.wait_for(
                    self._execute_chat_completion(request_params),
                    timeout=self.timeout
                )
                
                # Record success
                if self.circuit_breaker:
                    self.circuit_breaker.record_success(model)
                
                # Update metrics
                self._total_requests += 1
                if hasattr(response, "usage"):
                    self._total_tokens += response.usage.total_tokens
                
                return response
                
            except asyncio.TimeoutError as e:
                last_exception = LLMTimeoutError(
                    f"Request timed out after {self.timeout}s",
                    timeout_seconds=self.timeout,
                    model=model
                )
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                
            except Exception as e:
                last_exception = self._handle_exception(e, model, attempt)
                
                # Record failure for circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure(model)
                
                # Check if we should retry
                if not self._should_retry(last_exception, attempt):
                    break
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    backoff_time = min(2 ** attempt, 10)  # Max 10 seconds
                    logger.info(f"Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
        
        # All retries exhausted
        logger.error(f"All {self.max_retries} retry attempts failed")
        raise last_exception
    
    async def _execute_chat_completion(
        self,
        request_params: Dict[str, Any]
    ) -> LLMResponse:
        """Execute the actual chat completion call"""
        try:
            response = self.portkey.chat.completions.create(**request_params)
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content
            
            # Build usage info
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                finish_reason=choice.finish_reason,
                metadata={
                    "id": response.id,
                    "created": response.created,
                }
            )
            
        except Exception as e:
            logger.error(f"Portkey API error: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Union[Dict[str, str], ChatMessage]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream chat completion responses
        
        Args:
            messages: List of chat messages
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            metadata: Additional metadata
            **kwargs: Additional parameters
        
        Yields:
            Content chunks as they arrive
        
        Raises:
            LLMProviderError: Provider returned an error
            LLMTimeoutError: Request timed out
        """
        # Convert ChatMessage objects to dicts
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted_messages.append(msg.dict(exclude_none=True))
            else:
                formatted_messages.append(msg)
        
        # Build request parameters
        request_params = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True,
        }
        
        if max_tokens is not None:
            request_params["max_tokens"] = max_tokens
        if metadata:
            request_params["metadata"] = metadata
        
        request_params.update(kwargs)
        
        try:
            stream = self.portkey.chat.completions.create(**request_params)
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise self._handle_exception(e, model, 0)
    
    async def completion_with_prompt(
        self,
        prompt_id: str,
        variables: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute completion using Portkey prompt template
        
        Args:
            prompt_id: Portkey prompt template ID
            variables: Variables to substitute in prompt
            model: Override model from prompt template
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse with content and metadata
        
        Raises:
            PromptNotFoundError: Prompt template not found
            LLMProviderError: Provider returned an error
        """
        try:
            request_params = {
                "prompt_id": prompt_id,
                "variables": variables or {},
            }
            
            if model:
                request_params["model"] = model
            
            request_params.update(kwargs)
            
            response = self.portkey.prompts.completions.create(**request_params)
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content
            
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                finish_reason=choice.finish_reason,
                metadata={
                    "id": response.id,
                    "prompt_id": prompt_id,
                    "variables": variables,
                }
            )
            
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise PromptNotFoundError(
                    f"Prompt template '{prompt_id}' not found in Portkey",
                    prompt_id=prompt_id
                )
            raise self._handle_exception(e, model or "unknown", 0)
    
    def _handle_exception(
        self,
        exception: Exception,
        model: str,
        attempt: int
    ) -> LLMException:
        """Convert provider exceptions to LLM exceptions"""
        error_str = str(exception).lower()
        
        # Rate limit errors
        if "rate limit" in error_str or "429" in error_str:
            return LLMRateLimitError(
                f"Rate limit exceeded: {exception}",
                provider=model.split("-")[0] if "-" in model else "unknown",
                model=model,
                details={"attempt": attempt + 1}
            )
        
        # Timeout errors
        if "timeout" in error_str or "timed out" in error_str:
            return LLMTimeoutError(
                f"Request timed out: {exception}",
                timeout_seconds=self.timeout,
                model=model,
                details={"attempt": attempt + 1}
            )
        
        # Generic provider error
        return LLMProviderError(
            f"Provider error: {exception}",
            provider=model.split("-")[0] if "-" in model else "unknown",
            model=model,
            details={"attempt": attempt + 1, "error": str(exception)}
        )
    
    def _should_retry(self, exception: LLMException, attempt: int) -> bool:
        """Determine if request should be retried"""
        # Don't retry on last attempt
        if attempt >= self.max_retries - 1:
            return False
        
        # Retry on rate limits and timeouts
        if isinstance(exception, (LLMRateLimitError, LLMTimeoutError)):
            return True
        
        # Retry on provider errors (might be transient)
        if isinstance(exception, LLMProviderError):
            return True
        
        # Don't retry on validation or circuit breaker errors
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        return {
            "total_requests": self._total_requests,
            "total_tokens": self._total_tokens,
            "total_cost": self._total_cost,
            "circuit_breaker_states": {
                provider: self.circuit_breaker.get_state(provider)
                for provider in self.circuit_breaker._state.keys()
            } if self.circuit_breaker else {}
        }
