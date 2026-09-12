# Agent Tool Definitions

This document defines the logical deterministic capabilities (tools) exposed to the agents in the POC runtime.

## 1. Admissions Agent Tools

### `get_admission_offer`
* **Owning Domain**: Admissions
* **Purpose**: Retrieves the current status and details of a student's admission offer.
* **Input**: `student_id`
* **Output**: Offer details (Status, Expiration Date, Program).
* **Classification**: Deterministic / Read-Only.

### `evaluate_admission_requirements`
* **Owning Domain**: Admissions
* **Purpose**: Evaluates Admissions business rules (e.g., ADM-R02) to determine if preconditions like a deposit exist.
* **Input**: `student_id`, `offer_id`
* **Output**: List of requirements (e.g., `PaymentRequired`, amount).
* **Classification**: Deterministic rules engine.

### `delegate_student_payment`
* **Owning Domain**: Admissions (Delegation capability)
* **Purpose**: Constructs and sends a `StudentPaymentRequest` to the Fees & Payments Agent.
* **Input**: `student_id`, `amount`, `currency`, `idempotency_key`, `correlation_id`
* **Output**: `StudentPaymentResult` schema.
* **Classification**: Agent action (HTTP Invocation).

### `confirm_admission`
* **Owning Domain**: Admissions
* **Purpose**: Authoritatively transitions the student state to `Admission Confirmed`.
* **Input**: `student_id`, `offer_id`
* **Output**: Success confirmation.
* **Classification**: Deterministic / State-Mutating. Emits Business Event.

---

## 2. Fees & Payments Agent Tools

### `validate_payment_request`
* **Owning Domain**: Fees & Payments
* **Purpose**: Performs **business and authorization validation** (e.g., verifying the requesting domain is authorized, the operation is permitted, and the business context is valid). *Note: Structural schema validation (types, required fields) is performed automatically by Pydantic at the HTTP boundary before the agent ever receives the request.*
* **Input**: `StudentPaymentRequest` payload.
* **Output**: Validation result (True/False).
* **Classification**: Deterministic business validation.

### `collect_student_payment`
* **Owning Domain**: Fees & Payments
* **Purpose**: A deterministic POC workflow/capability composition that internally coordinates Student Financial Obligation Management, Payment Collection, Payment Status Management, and Receipting/Reconciliation.
* **Input**: `student_id`, `amount`, `idempotency_key`
* **Output**: `ReceiptID`, `PaymentStatus`
* **Classification**: Deterministic / State-Mutating Composition.
* **Idempotency Requirement**: MUST reject duplicate executions for the same `idempotency_key`.

---

## 3. Internal Runtime Operations (Not LLM Tools)

### `issue_payment_result`
* **Purpose**: Constructs the final structured response payload (`StudentPaymentResult`) to return to the calling agent via HTTP. This is a transport/runtime operation executed by the agent runtime *after* the agent decides the payment result. It is NOT exposed as an LLM reasoning tool.
