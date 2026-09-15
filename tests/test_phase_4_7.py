import unittest
from unittest.mock import patch, MagicMock

from xsc_lib.xsc_lib_common.xsc_libc_exceptions import EntityNotFoundError, ValidationException

from modules.m_admissions.tools.admissions_tools import (
    get_admissions_agent_tools,
    GetAdmissionOfferTool,
    EvaluateAdmissionRequirementsTool,
    DelegateStudentPaymentTool,
    ConfirmAdmissionTool
)
from modules.m_fees_payments.tools.fees_payments_tools import (
    get_fees_payments_agent_tools,
    ValidatePaymentRequestTool,
    CollectStudentPaymentTool
)

class TestPhase47LangChainTools(unittest.TestCase):

    def setUp(self):
        self.mock_adm_caps = MagicMock()
        self.mock_fees_caps = MagicMock()
        
        self.adm_tools = get_admissions_agent_tools(self.mock_adm_caps)
        self.fees_tools = get_fees_payments_agent_tools(self.mock_fees_caps)

    def test_tool_registration_and_naming(self):
        """Verify all 6 tools are registered with their canonical names and issue_payment_result is absent."""
        adm_tool_names = [tool.name for tool in self.adm_tools]
        fees_tool_names = [tool.name for tool in self.fees_tools]
        
        self.assertCountEqual(adm_tool_names, [
            "get_admission_offer", 
            "evaluate_admission_requirements",
            "delegate_student_payment",
            "confirm_admission"
        ])
        
        self.assertCountEqual(fees_tool_names, [
            "validate_payment_request",
            "collect_student_payment"
        ])
        
        all_tool_names = adm_tool_names + fees_tool_names
        self.assertNotIn("issue_payment_result", all_tool_names)

    def test_authorization_matrix(self):
        """Verify cross-domain tools cannot be accessed by unauthorized agents."""
        # By definition of our factory functions, they only return the authorized tools.
        adm_tool_names = [tool.name for tool in self.adm_tools]
        fees_tool_names = [tool.name for tool in self.fees_tools]

        for name in fees_tool_names:
            self.assertNotIn(name, adm_tool_names)
            
        for name in adm_tool_names:
            self.assertNotIn(name, fees_tool_names)

    def test_get_admission_offer_tool_success(self):
        """Verify capability delegation and structured result for successful get_admission_offer."""
        tool = next(t for t in self.adm_tools if t.name == "get_admission_offer")
        
        # Mock the deterministic capability return
        mock_offer = MagicMock()
        mock_offer.offer_id = "O-1"
        mock_offer.student_id = "S-1"
        mock_offer.program_id = "P-1"
        mock_offer.status = "Issued"
        mock_offer.payment_required = True
        mock_offer.payment_amount = 500.00
        mock_offer.currency = "USD"
        mock_offer.expiration_date = None
        self.mock_adm_caps.get_admission_offer.return_value = mock_offer
        
        # Invoke tool using the dict format mimicking LangChain's invocation
        result = tool.invoke({"offer_id": "O-1"})
        
        # Verify capability delegation
        self.mock_adm_caps.get_admission_offer.assert_called_once_with("O-1")
        
        # Verify structured result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["offer_id"], "O-1")
        self.assertEqual(result["data"]["status"], "Issued")

    def test_get_admission_offer_tool_failure(self):
        """Verify errors are handled and not converted to false success."""
        tool = next(t for t in self.adm_tools if t.name == "get_admission_offer")
        
        # Mock error
        self.mock_adm_caps.get_admission_offer.side_effect = EntityNotFoundError("Admission offer not found: MISSING")
        
        result = tool.invoke({"offer_id": "MISSING"})
        
        self.mock_adm_caps.get_admission_offer.assert_called_once_with("MISSING")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "EntityNotFoundError")
        self.assertIn("MISSING", result["message"])

    @patch("modules.m_admissions.clients.fees_payments_client.FeesPaymentsClient")
    def test_delegate_student_payment_tool(self, mock_client_cls):
        """Verify delegate_student_payment integrates correctly via client."""
        # Setup mock client to return a valid StudentPaymentResult
        mock_client = MagicMock()
        from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentResult
        from datetime import datetime, timezone
        mock_client.delegate_payment.return_value = StudentPaymentResult(
            ContractVersion="1.0",
            CorrelationID="corr-47-test",
            IdempotencyKey="test-idem-999",
            RequestStatus="Completed",
            PaymentStatus="Success",
            ReceiptID="RCPT-123",
            Timestamp=datetime.now(timezone.utc)
        )
        mock_client_cls.return_value = mock_client

        tool = next(t for t in self.adm_tools if t.name == "delegate_student_payment")
        
        result = tool.invoke(
            {
                "student_id": "S-999",
                "amount": 1250.0,
                "idempotency_key": "test-idem-999",
                "currency": "USD"
            },
            config={"metadata": {"correlation_id": "corr-47-test"}}
        )
        
        self.assertEqual(result["status"], "success")
        data = result["data"]
        
        # Verify canonical fields returned from the mock client
        self.assertEqual(data["ContractVersion"], "1.0")
        self.assertEqual(data["CorrelationID"], "corr-47-test")
        self.assertEqual(data["IdempotencyKey"], "test-idem-999")
        self.assertEqual(data["PaymentStatus"], "Success")

    def test_validate_payment_request_tool(self):
        """Verify validate_payment_request tool passes payload correctly and handles ValidationException."""
        tool = next(t for t in self.fees_tools if t.name == "validate_payment_request")
        
        self.mock_fees_caps.validate_payment_request.side_effect = ValidationException("Unauthorized domain")
        
        payload = {
            "ContractVersion": "1.0",
            "RequestingDomain": "InvalidDomain",
            "RequestingAgent": "AdmissionsAgent",
            "CorrelationID": "corr-1",
            "IdempotencyKey": "idem-1",
            "StudentID": "S-1",
            "ObligationType": "AdmissionFee",
            "Amount": 500.00,
            "Currency": "USD",
            "Timestamp": "2026-09-15T10:00:00Z"
        }
        
        result = tool.invoke({"request_payload": payload})
        
        # Check error wrapping
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "ValidationException")
        
        # Verify it constructed the pydantic model and called capability
        called_args = self.mock_fees_caps.validate_payment_request.call_args
        self.assertIsNotNone(called_args)
        arg_obj = called_args[0][0]
        self.assertEqual(arg_obj.requesting_domain, "InvalidDomain")

if __name__ == '__main__':
    unittest.main()
