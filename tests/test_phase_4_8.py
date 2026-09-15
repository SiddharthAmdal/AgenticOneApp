import json
import unittest
from unittest.mock import MagicMock

from xsc_lib.xsc_lib_common.nim_adapter import NIMAdapter, LLMMessage, LLMToolCall, LLMResponse

from modules.m_admissions.agents.admissions_agent import AdmissionsAgent
from modules.m_fees_payments.agents.fees_payments_agent import FeesPaymentsAgent
from modules.m_admissions.tools.admissions_tools import get_admissions_agent_tools
from modules.m_fees_payments.tools.fees_payments_tools import get_fees_payments_agent_tools

class TestPhase48AgentWorkflows(unittest.TestCase):

    def setUp(self):
        self.mock_adm_caps = MagicMock()
        self.mock_fees_caps = MagicMock()
        self.mock_nim_adapter = MagicMock(spec=NIMAdapter)

        self.adm_agent = AdmissionsAgent(self.mock_adm_caps, self.mock_nim_adapter)
        self.fees_agent = FeesPaymentsAgent(self.mock_fees_caps, self.mock_nim_adapter)

    def test_agent_construction_and_tool_authorization(self):
        """Verify agents construct successfully and possess strictly authorized tools."""
        self.assertIsNotNone(self.adm_agent)
        self.assertIsNotNone(self.fees_agent)

        self.assertEqual(len(self.adm_agent.tools), 4)
        self.assertCountEqual(
            list(self.adm_agent.tools.keys()),
            ["get_admission_offer", "evaluate_admission_requirements", "delegate_student_payment", "confirm_admission"]
        )

        self.assertEqual(len(self.fees_agent.tools), 2)
        self.assertCountEqual(
            list(self.fees_agent.tools.keys()),
            ["validate_payment_request", "collect_student_payment"]
        )

    def test_graph_structure(self):
        """Verify the graph compiles and has expected nodes and safeguards."""
        # Check admissions graph structure
        adm_nodes = list(self.adm_agent.graph.nodes.keys())
        self.assertIn("agent", adm_nodes)
        self.assertIn("execute_tools", adm_nodes)
        
        fees_nodes = list(self.fees_agent.graph.nodes.keys())
        self.assertIn("agent", fees_nodes)
        self.assertIn("execute_tools", fees_nodes)

    def test_admissions_valid_offer_no_payment(self):
        """Test the path where an offer is valid and requires no payment (direct to confirmation)."""
        # We need to simulate the LLM's multi-step responses.
        # Step 1: LLM calls evaluate_admission_requirements
        # Step 2: LLM calls confirm_admission
        # Step 3: LLM returns final structured response
        
        step_1_res = LLMResponse(
            tool_calls=[LLMToolCall(id="t-1", type="function", function_name="evaluate_admission_requirements", arguments='{"offer_id": "O-1"}')]
        )
        step_2_res = LLMResponse(
            tool_calls=[LLMToolCall(id="t-2", type="function", function_name="confirm_admission", arguments='{"offer_id": "O-1"}')]
        )
        step_3_res = LLMResponse(
            content=json.dumps({"status": "success", "message": "Admission confirmed"})
        )
        
        self.mock_nim_adapter.generate_response.side_effect = [step_1_res, step_2_res, step_3_res]
        
        # Tool capability mock returns success
        self.mock_adm_caps.evaluate_admission_requirements.return_value = {"valid": True, "payment_required": False}
        self.mock_adm_caps.confirm_admission.return_value = None
        
        state = self.adm_agent.invoke({"offer_id": "O-1", "messages": [LLMMessage(role="user", content="Process O-1")]})
        
        # Verify
        self.assertIsNotNone(state.get("final_result"))
        self.assertEqual(state["final_result"]["status"], "success")
        
        # Capability assertions
        self.mock_adm_caps.evaluate_admission_requirements.assert_called_once_with("O-1")
        self.mock_adm_caps.confirm_admission.assert_called_once_with("O-1", None)

    def test_admissions_payment_required_successful(self):
        """Test valid offer + payment required + successful payment -> confirmation path."""
        # 1: Evaluate
        # 2: Delegate payment
        # 3: Confirm admission (with payment result)
        # 4: Final response
        
        step_1 = LLMResponse(tool_calls=[LLMToolCall(id="t-1", type="function", function_name="evaluate_admission_requirements", arguments='{"offer_id": "O-2"}')])
        step_2 = LLMResponse(tool_calls=[LLMToolCall(id="t-2", type="function", function_name="delegate_student_payment", arguments='{"student_id": "S-2", "amount": 500, "currency": "USD", "idempotency_key": "IDEM"}')])
        valid_payment_result = {
            "ContractVersion": "1.0",
            "PaymentID": "P-123",
            "CorrelationID": "corr-1",
            "IdempotencyKey": "idem-1",
            "StudentID": "S-2",
            "RequestStatus": "Completed",
            "PaymentStatus": "Success",
            "AmountCollected": 500.0,
            "Currency": "USD",
            "Timestamp": "2026-09-15T10:00:00Z"
        }
        step_3 = LLMResponse(tool_calls=[LLMToolCall(id="t-3", type="function", function_name="confirm_admission", arguments=json.dumps({"offer_id": "O-2", "payment_result": valid_payment_result}))])
        step_4 = LLMResponse(content='{"status": "success", "message": "Confirmed with payment"}')
        
        self.mock_nim_adapter.generate_response.side_effect = [step_1, step_2, step_3, step_4]
        self.mock_adm_caps.evaluate_admission_requirements.return_value = {"valid": True, "payment_required": True}
        self.mock_adm_caps.confirm_admission.return_value = None
        
        state = self.adm_agent.invoke({"offer_id": "O-2", "messages": [LLMMessage(role="user", content="Process O-2")]})
        
        self.assertEqual(state["final_result"]["status"], "success")
        
        # Assert confirm admission got a payment context
        self.mock_adm_caps.confirm_admission.assert_called_once()

    def test_fees_payments_behavior_success(self):
        """Test Fees & Payments Agent processes a valid request and collects payment."""
        # 1: validate_payment_request
        # 2: collect_student_payment
        # 3: Final Response
        
        req_payload = {
            "ContractVersion": "1.0", 
            "RequestingDomain": "Admissions",
            "RequestingAgent": "AdmissionsAgent",
            "CorrelationID": "corr-1",
            "IdempotencyKey": "idem-1",
            "StudentID": "S-1",
            "ObligationType": "AdmissionFee",
            "Amount": 500.0, 
            "Currency": "USD",
            "Timestamp": "2026-09-15T10:00:00Z"
        }
        
        step_1 = LLMResponse(tool_calls=[LLMToolCall(id="f-1", type="function", function_name="validate_payment_request", arguments=json.dumps({"request_payload": req_payload}))])
        step_2 = LLMResponse(tool_calls=[LLMToolCall(id="f-2", type="function", function_name="collect_student_payment", arguments=json.dumps({"request_payload": req_payload}))])
        step_3 = LLMResponse(content='{"status": "success", "data": {"payment_id": "P-1"}}')
        
        self.mock_nim_adapter.generate_response.side_effect = [step_1, step_2, step_3]
        
        # Mock cap
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"payment_id": "P-1"}
        self.mock_fees_caps.collect_student_payment.return_value = mock_result
        
        state = self.fees_agent.invoke({"request_payload": req_payload})
        
        self.assertEqual(state["final_result"]["status"], "success")
        self.mock_fees_caps.validate_payment_request.assert_called_once()
        self.mock_fees_caps.collect_student_payment.assert_called_once()

    def test_max_iteration_safeguard(self):
        """Verify the workflow terminates gracefully to prevent infinite tool loops."""
        # Always return a tool call to simulate a broken LLM stuck in a loop
        step = LLMResponse(tool_calls=[LLMToolCall(id="t-loop", type="function", function_name="get_admission_offer", arguments='{"offer_id": "O-1"}')])
        
        self.mock_nim_adapter.generate_response.return_value = step
        
        state = self.adm_agent.invoke({"offer_id": "O-1", "messages": []})
        
        # Should hit max iterations
        self.assertIsNotNone(state.get("error"))
        self.assertEqual(state["error"], "Max iterations reached")

if __name__ == '__main__':
    unittest.main()
