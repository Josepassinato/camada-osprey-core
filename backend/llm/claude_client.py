"""
Gemini LLM Client (formerly Claude)

Uses Google Gemini 2.5 Flash for all specialized agents.
Keeps the same ClaudeClient class name and chat() interface
so that all agent imports remain unchanged.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("EMERGENT_LLM_KEY")
    or os.environ.get("GOOGLE_API_KEY")
)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_MODEL = "gemini-2.5-flash"
MAX_TOKENS_DEFAULT = 8192


class ClaudeClient:
    """Async client wrapping Google Gemini (same interface as the old Anthropic client)."""

    def __init__(self, api_key: Optional[str] = None, default_model: str = DEFAULT_MODEL):
        key = api_key or GEMINI_API_KEY
        if key and not GEMINI_API_KEY:
            genai.configure(api_key=key)
        self.default_model = default_model

    async def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = MAX_TOKENS_DEFAULT,
    ) -> Dict[str, Any]:
        """
        Send a chat request to Gemini.

        Args:
            system: System prompt (passed as system_instruction)
            messages: List of {"role": "user"|"assistant", "content": "..."}
            model: Model ID (defaults to gemini-2.5-flash)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Dict with "content", "model", "input_tokens", "output_tokens"
        """
        model_name = model or self.default_model
        start = time.time()

        try:
            gemini_model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )

            # Build the user prompt from messages
            # Gemini expects a single string or list of parts for generate_content
            user_content = "\n".join(
                msg["content"] for msg in messages if msg.get("role") == "user"
            )

            response = gemini_model.generate_content(user_content)

            content = response.text if response.text else ""
            latency_ms = (time.time() - start) * 1000

            # Extract token counts if available
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

            logger.info(
                f"Gemini call: model={model_name}, "
                f"tokens={input_tokens}+{output_tokens}, "
                f"latency={latency_ms:.0f}ms"
            )

            return {
                "content": content,
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
            }

        except Exception as e:
            logger.error(f"Gemini error: {e}", exc_info=True)
            raise
