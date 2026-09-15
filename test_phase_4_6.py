import os
import unittest
from unittest.mock import patch, MagicMock

import openai

from xsc_lib.xsc_lib_common.xsc_libc_exceptions import (
    ConfigurationError,
    ProviderAuthenticationError,
    ProviderTimeoutError,
    ProviderServerError,
    ProviderRequestError
)
from xsc_lib.xsc_lib_common.nim_adapter import (
    NIMAdapter,
    LLMMessage,
    LLMToolCall,
    LLMResponse,
    LLMUsage
)

class TestPhase46NIMAdapter(unittest.TestCase):
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_raises_configuration_error(self):
        """Verify that missing API key raises ConfigurationError safely without trying to connect."""
        with self.assertRaises(ConfigurationError) as ctx:
            NIMAdapter()
        self.assertIn("NVIDIA NIM API key is missing", str(ctx.exception))

    @patch.dict(os.environ, {
        "NVIDIA_NIM_API_KEY": "fake_key",
        "NVIDIA_NIM_BASE_URL": "http://fake-url.com",
        "NVIDIA_NIM_MODEL": "test/model-1"
    }, clear=True)
    def test_adapter_initialization(self):
        """Verify adapter initializes correctly from configuration."""
        adapter = NIMAdapter()
        self.assertEqual(adapter.api_key, "fake_key")
        self.assertEqual(adapter.base_url, "http://fake-url.com")
        self.assertEqual(adapter.model, "test/model-1")

    @patch.dict(os.environ, {"NVIDIA_NIM_API_KEY": "fake_key"}, clear=True)
    @patch('xsc_lib.xsc_lib_common.nim_adapter.OpenAI')
    def test_successful_invocation(self, mock_openai_class):
        """Verify successful normalization of provider response."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Setup mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Here is the response"
        mock_choice.message.tool_calls = None
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]
        
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client.chat.completions.create.return_value = mock_response

        adapter = NIMAdapter()
        messages = [LLMMessage(role="user", content="Hello")]
        response = adapter.generate_response(messages)

        # Assert normalize response
        self.assertEqual(response.content, "Here is the response")
        self.assertEqual(response.finish_reason, "stop")
        self.assertIsNone(response.tool_calls)
        self.assertEqual(response.usage.prompt_tokens, 10)
        self.assertEqual(response.usage.completion_tokens, 20)
        self.assertEqual(response.usage.total_tokens, 30)
        
        # Verify provider translation
        mock_client.chat.completions.create.assert_called_once_with(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": "Hello"}]
        )

    @patch.dict(os.environ, {"NVIDIA_NIM_API_KEY": "fake_key"}, clear=True)
    @patch('xsc_lib.xsc_lib_common.nim_adapter.OpenAI')
    def test_tool_call_normalization(self, mock_openai_class):
        """Verify tool calls are parsed and normalized without leaking private structs."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Setup mock response with tool calls
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_choice.finish_reason = "tool_calls"
        
        mock_tc = MagicMock()
        mock_tc.id = "call_123"
        mock_tc.type = "function"
        mock_tc.function.name = "get_admission_offer"
        mock_tc.function.arguments = '{"offer_id": "O-1"}'
        
        mock_choice.message.tool_calls = [mock_tc]
        mock_response.choices = [mock_choice]
        mock_response.usage = None

        mock_client.chat.completions.create.return_value = mock_response

        adapter = NIMAdapter()
        messages = [LLMMessage(role="user", content="Call tool")]
        tools = [{"type": "function", "function": {"name": "get_admission_offer"}}]
        
        response = adapter.generate_response(messages, tools=tools)

        # Assert normalize response
        self.assertIsNone(response.content)
        self.assertEqual(response.finish_reason, "tool_calls")
        self.assertIsNotNone(response.tool_calls)
        self.assertEqual(len(response.tool_calls), 1)
        
        tc = response.tool_calls[0]
        self.assertEqual(tc.id, "call_123")
        self.assertEqual(tc.type, "function")
        self.assertEqual(tc.function_name, "get_admission_offer")
        self.assertEqual(tc.arguments, '{"offer_id": "O-1"}')

    @patch.dict(os.environ, {"NVIDIA_NIM_API_KEY": "fake_key"}, clear=True)
    @patch('xsc_lib.xsc_lib_common.nim_adapter.OpenAI')
    def test_provider_errors_translated(self, mock_openai_class):
        """Verify provider errors are translated to application exceptions."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        adapter = NIMAdapter()
        messages = [LLMMessage(role="user", content="Hello")]

        # 1. Authentication
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Invalid Key",
            response=MagicMock(),
            body={}
        )
        with self.assertRaises(ProviderAuthenticationError):
            adapter.generate_response(messages)

        # 2. Timeout
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError(
            request=MagicMock()
        )
        with self.assertRaises(ProviderTimeoutError):
            adapter.generate_response(messages)

        # 3. Request Error (Bad Request)
        mock_client.chat.completions.create.side_effect = openai.BadRequestError(
            message="Bad format",
            response=MagicMock(),
            body={}
        )
        with self.assertRaises(ProviderRequestError):
            adapter.generate_response(messages)
            
        # 4. Server Error
        mock_client.chat.completions.create.side_effect = openai.InternalServerError(
            message="Overloaded",
            response=MagicMock(),
            body={}
        )
        with self.assertRaises(ProviderServerError):
            adapter.generate_response(messages)

if __name__ == '__main__':
    unittest.main()
