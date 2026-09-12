# Agent Contracts

This document defines the conceptual structured contracts for inter-agent communication within the POC. Agent communication is exclusively structured and explicit; conversational prompt-to-prompt text is prohibited for cross-domain delegation.

## 1. Request, Operation, and Workflow Identity

To prevent traceability confusion, the following identifiers are strictly distinguished:

* **User Request ID**: Traces the user's interaction session. Owned by the entry/gateway layer. Optional for backend agent-to-agent contracts.
* **Correlation ID**: Identifies and traces the *overall business workflow* across multiple domains and agents (e.g., `CORR-847291`). Owned by the originating agent (Admissions). Required in all agent contracts.
* **Idempotency Key**: Identifies a *specific operation* to prevent duplicate execution (e.g., `IDEMP-ADM-PAY-938472`). Owned by the requesting agent for a specific action. Required for operations that mutate state (payment collection).
* **Business Transaction ID**: The canonical system receipt ID generated after successful execution. Owned by the fulfilling domain (Fees & Payments).

## 2. Contract Versioning Principles

All structured contracts must support evolution.
* **ContractName**: Identifies the schema (e.g., `StudentPaymentRequest`).
* **ContractVersion**: Semantic version (e.g., `1.0`).
* **Compatibility Expectations**: Consumers must ignore unrecognized optional fields. Producers must provide all required fields.

## 3. Admissions → Fees & Payments: Student Payment Request

**Producer**: Admissions Agent  
**Consumer**: Fees & Payments Agent  
**Validation**: Fees & Payments Agent (rejects if malformed)

| Field | Type | Required | Purpose |
| :--- | :--- | :--- | :--- |
| `ContractVersion` | String | Yes | E.g., "1.0" |
| `RequestingDomain` | String | Yes | Identifies the authorized caller ("Admissions"). |
| `RequestingAgent` | String | Yes | Identifies the specific agent identity. |
| `CorrelationID` | String | Yes | Traces the overarching admission confirmation workflow. |
| `IdempotencyKey` | String | Yes | Protects Fees & Payments from executing this exact charge twice if retried. |
| `StudentID` | String | Yes | Target user for the obligation. |
| `ObligationType` | String | Yes | E.g., "AdmissionDeposit". |
| `Amount` | Numeric | Yes | The required payment amount. |
| `Currency` | String | Yes | E.g., "USD". |
| `BusinessReason` | String | Optional | Audit trail context. |
| `Timestamp` | ISO8601 | Yes | Time of request generation. |

## 4. Fees & Payments → Admissions: Student Payment Result

**Producer**: Fees & Payments Agent  
**Consumer**: Admissions Agent  
**Validation**: Admissions Agent

| Field | Type | Required | Purpose |
| :--- | :--- | :--- | :--- |
| `ContractVersion` | String | Yes | E.g., "1.0" |
| `CorrelationID` | String | Yes | Matches the overarching workflow. |
| `IdempotencyKey` | String | Yes | Matches the specific operation requested. |
| `RequestStatus` | String | Yes | Infrastructure/Processing status (`Completed`, `Invalid`, `Failed`). |
| `PaymentStatus` | String | Yes | Business status of the payment (`Success`, `Declined`, `Pending`, `NotAttempted`). |
| `ReceiptID` | String | Optional | The Business Transaction ID (Receipt reference) if successful. |
| `FailureReason` | String | Optional | Human/Agent readable context if `RequestStatus` or `PaymentStatus` is not success. |
| `Timestamp` | ISO8601 | Yes | Time of result generation. |

## 5. Business vs. Technical Events

* **Technical Event**: e.g., `HTTP 200`, `Message Delivered`. This only means the agent successfully received the contract. It does NOT mean the business operation succeeded.
* **Business Event**: e.g., `Payment Confirmed`. This is the canonical domain state change that occurs *after* successful deterministic execution. Agents react to business events and payload statuses, not just technical transport successes.
