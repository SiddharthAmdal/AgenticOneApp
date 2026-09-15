import json
import os
import unittest
from unittest.mock import MagicMock
from xsc_lib.xsc_lib_common.nim_adapter import NIMAdapter, LLMMessage
from xsc_lib.xsc_lib_common.xsc_libc_tracer import DevelopmentTracer

class TestPhase411ReasoningTrace(unittest.TestCase):
    def setUp(self):
        self.trace_file = DevelopmentTracer.TRACE_FILE
        if os.path.exists(self.trace_file):
            os.remove(self.trace_file)

    def tearDown(self):
        if os.path.exists(self.trace_file):
            os.remove(self.trace_file)

    def test_reasoning_in_model_extra(self):
        """Test extraction of reasoning_content from model_extra (OpenAI pattern)."""
        adapter = NIMAdapter(api_key="mock", base_url="http://mock")
        
        # Mock the choice/message structure
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Final answer"
        mock_message.tool_calls = None
        mock_message.model_extra = {"reasoning_content": "Internal thought process"}
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        
        mock_response.choices = [mock_choice]
        mock_response.usage = None
        
        adapter.client.chat.completions.create = MagicMock(return_value=mock_response)
        
        res = adapter.generate_response(
            [LLMMessage(role="user", content="hello")],
            trace_context={"correlation_id": "c-123"}
        )
        
        self.assertEqual(res.content, "Final answer")
        
        # Verify trace file
        self.assertTrue(os.path.exists(self.trace_file))
        with open(self.trace_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            trace = json.loads(lines[0])
            self.assertTrue(trace["ReasoningAvailable"])
            self.assertEqual(trace["ReasoningContent"], "Internal thought process")
            self.assertEqual(trace["CorrelationID"], "c-123")

    def test_reasoning_in_think_tags(self):
        """Test extraction of reasoning_content from <think> tags (Open-weight pattern)."""
        adapter = NIMAdapter(api_key="mock", base_url="http://mock")
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "<think>\nThinking step by step\n</think>\nFinal answer"
        mock_message.tool_calls = None
        mock_message.model_extra = {}
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        
        mock_response.choices = [mock_choice]
        mock_response.usage = None
        
        adapter.client.chat.completions.create = MagicMock(return_value=mock_response)
        
        res = adapter.generate_response(
            [LLMMessage(role="user", content="hello")],
            trace_context={"correlation_id": "c-123", "domain": "Admissions"}
        )
        
        self.assertEqual(res.content, "Final answer")
        
        # Verify trace file
        self.assertTrue(os.path.exists(self.trace_file))
        with open(self.trace_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            trace = json.loads(lines[0])
            self.assertTrue(trace["ReasoningAvailable"])
            self.assertEqual(trace["ReasoningContent"], "Thinking step by step")
            self.assertEqual(trace["Domain"], "Admissions")

    def test_no_reasoning(self):
        """Test behavior when no reasoning trace is available."""
        adapter = NIMAdapter(api_key="mock", base_url="http://mock")
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Just final answer"
        mock_message.tool_calls = None
        mock_message.model_extra = {}
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        
        mock_response.choices = [mock_choice]
        mock_response.usage = None
        
        adapter.client.chat.completions.create = MagicMock(return_value=mock_response)
        
        res = adapter.generate_response(
            [LLMMessage(role="user", content="hello")],
            trace_context={"correlation_id": "c-123"}
        )
        
        self.assertEqual(res.content, "Just final answer")
        
        with open(self.trace_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            trace = json.loads(lines[0])
            self.assertFalse(trace["ReasoningAvailable"])
            self.assertIsNone(trace["ReasoningContent"])

if __name__ == '__main__':
    unittest.main()
