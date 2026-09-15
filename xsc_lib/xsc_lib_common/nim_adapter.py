import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

import openai
from openai import OpenAI

from xsc_lib.xsc_lib_common.xsc_libc_exceptions import (
    ConfigurationError,
    ProviderAuthenticationError,
    ProviderTimeoutError,
    ProviderServerError,
    ProviderRequestError
)
import re
from xsc_lib.xsc_lib_common.xsc_libc_tracer import DevelopmentTracer


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMToolCall(BaseModel):
    id: str
    type: str
    function_name: str
    arguments: str  # JSON string of arguments


class LLMUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    content: Optional[str] = None
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[LLMToolCall]] = None
    usage: Optional[LLMUsage] = None


class NIMAdapter:
    """
    Adapter for NVIDIA NIM LLM endpoints.
    Provides a clean abstraction over the concrete OpenAI-compatible provider.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, timeout: float = 30.0):
        # Resolve config from args or environment
        self.api_key = api_key or os.getenv("NVIDIA_NIM_API_KEY")
        self.base_url = base_url or os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model = model or os.getenv("NVIDIA_NIM_MODEL", "openai/gpt-oss-20b")
        self.timeout = timeout

        if not self.api_key:
            raise ConfigurationError("NVIDIA NIM API key is missing. Ensure NVIDIA_NIM_API_KEY is set in the environment.")

        # Initialize the synchronous OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def generate_response(
        self, 
        messages: List[LLMMessage], 
        tools: Optional[List[Dict[str, Any]]] = None,
        trace_context: Optional[dict] = None
    ) -> LLMResponse:
        """
        Sends a request to the NIM model and returns a normalized response.
        Extracts reasoning traces if available and logs them to the development tracer.
        """
        # Translate internal messages to provider format
        provider_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Prepare kwargs
        kwargs = {
            "model": self.model,
            "messages": provider_messages,
        }
        if tools:
            kwargs["tools"] = tools

        try:
            response = self.client.chat.completions.create(**kwargs)
            return self._normalize_response(response, trace_context)

        except openai.AuthenticationError as e:
            raise ProviderAuthenticationError(f"Authentication failed: {str(e)}")
        except openai.APITimeoutError as e:
            raise ProviderTimeoutError(f"Request timed out: {str(e)}")
        except openai.InternalServerError as e:
            raise ProviderServerError(f"Provider internal error: {str(e)}")
        except openai.RateLimitError as e:
            raise ProviderServerError(f"Rate limit exceeded: {str(e)}")
        except openai.APIConnectionError as e:
            raise ProviderServerError(f"Connection failed: {str(e)}")
        except openai.BadRequestError as e:
            raise ProviderRequestError(f"Invalid request: {str(e)}")
        except openai.APIStatusError as e:
            # Fallback for other status errors
            if e.status_code and e.status_code >= 500:
                raise ProviderServerError(f"Provider server error ({e.status_code}): {str(e)}")
            else:
                raise ProviderRequestError(f"Provider request error ({e.status_code}): {str(e)}")
        except Exception as e:
            # Catch unexpected errors to prevent leaking raw provider details uncontrollably,
            # but allow raising if it's completely out of bounds.
            raise ProviderServerError(f"Unexpected provider error: {str(e)}")

    def _normalize_response(self, response: Any, trace_context: Optional[dict] = None) -> LLMResponse:
        """
        Normalizes the provider response into the internal LLMResponse model.
        Also intercepts and logs reasoning traces if available.
        """
        choice = response.choices[0]
        message = choice.message

        content = message.content or ""
        reasoning_content = None

        # Check for reasoning_content in model_extra (OpenAI SDK pattern for some models)
        if getattr(message, "model_extra", None):
            reasoning_content = message.model_extra.get("reasoning_content")

        # Check for <think> tags embedded in content (Open-weight model pattern)
        if not reasoning_content and "<think>" in content:
            # Extract content between <think> and </think>
            match = re.search(r"<think>(.*?)</think>", content, flags=re.DOTALL)
            if match:
                reasoning_content = match.group(1).strip()
                # Remove the think block from the canonical content
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        
        # Log to development tracer
        reasoning_available = bool(reasoning_content)
        
        # Enhance context with model info
        log_ctx = dict(trace_context or {})
        log_ctx["model"] = self.model
        
        DevelopmentTracer.log_trace(
            reasoning_available=reasoning_available,
            reasoning_content=reasoning_content,
            context=log_ctx
        )

        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                LLMToolCall(
                    id=tc.id,
                    type=tc.type,
                    function_name=tc.function.name,
                    arguments=tc.function.arguments
                )
                for tc in message.tool_calls
            ]

        usage = None
        if response.usage:
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )

        return LLMResponse(
            content=content if content else None,
            finish_reason=choice.finish_reason,
            tool_calls=tool_calls,
            usage=usage
        )
