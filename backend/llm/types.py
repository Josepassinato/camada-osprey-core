"""
LLM Type Definitions

Data models for LLM requests, responses, and metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message role types for chat completions"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    
    class Config:
        use_enum_values = True


class LLMRequest(BaseModel):
    """Request model for LLM operations"""
    messages: List[ChatMessage]
    model: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = None
    prompt_id: Optional[str] = None
    stream: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ],
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }


class LLMUsage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    """Response model from LLM operations"""
    content: str
    model: str
    usage: LLMUsage
    finish_reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello! How can I help you today?",
                "model": "gpt-4o",
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                    "total_tokens": 30
                },
                "finish_reason": "stop",
                "metadata": {}
            }
        }


class PromptMetadata(BaseModel):
    """Metadata for prompts migrated to Portkey"""
    prompt_id: str = Field(..., description="Internal prompt identifier")
    portkey_id: Optional[str] = Field(None, description="Portkey prompt ID once created")
    name: str = Field(..., description="Human-readable prompt name")
    description: str = Field(..., description="Purpose and usage of the prompt")
    model: str = Field(default="gpt-4o", description="Recommended model for this prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    variables: List[str] = Field(default_factory=list, description="Variable names used in prompt")
    source_file: str = Field(..., description="Original source file path")
    source_line: int = Field(..., description="Line number in source file")
    migrated: bool = Field(default=False, description="Whether migrated to Portkey")
    migration_date: Optional[datetime] = Field(None, description="Date of migration to Portkey")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt_id": "maria_greeting",
                "portkey_id": "pp-maria-greeting-v1",
                "name": "Maria Greeting Prompt",
                "description": "Initial greeting message for Maria assistant",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500,
                "variables": ["user_name", "language"],
                "source_file": "backend/agents/maria/agent.py",
                "source_line": 45,
                "migrated": True,
                "migration_date": "2026-01-13T10:00:00Z",
                "tags": ["maria", "greeting", "conversational"]
            }
        }


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    COHERE = "cohere"


class ModelConfig(BaseModel):
    """Configuration for a specific model"""
    name: str
    provider: LLMProvider
    max_tokens: int = 4096
    temperature: float = 0.7
    fallback_models: List[str] = Field(default_factory=list)
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    supports_streaming: bool = True
    supports_function_calling: bool = False
    context_window: int = 4096
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "gpt-4o",
                "provider": "openai",
                "max_tokens": 4096,
                "temperature": 0.7,
                "fallback_models": ["gpt-4-turbo", "gpt-3.5-turbo"],
                "cost_per_1k_input_tokens": 0.005,
                "cost_per_1k_output_tokens": 0.015,
                "supports_streaming": True,
                "supports_function_calling": True,
                "context_window": 128000
            }
        }
