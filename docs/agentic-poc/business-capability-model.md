# POC Business Capability Model

This document refines the initial capability inventory into a rigorous capability model specifically for the Admissions and Finance domains participating in this POC. 

Capabilities represent stable business abilities, not specific technical APIs or AI agents.

## Execution Classifications

To describe how a capability is intended to execute, we use the following consistent classifications:
* **Agent-assisted**: An agent participates in the process but the substantive operation is performed by another deterministic service, workflow, or human.
* **Agent-executed**: The agent itself performs an authorized action through its runtime/tooling, where the action is explicitly within the agent's responsibility.
* **Deterministic service**: A deterministic capability/service performs a business operation according to explicit rules and controlled inputs, without relying on free-form LLM reasoning for the operation itself.
* **Workflow**: A predefined sequence/orchestration of deterministic or agent actions.
* **Human decision/approval**: A decision or approval that requires an authorized human actor.

## 1. Admissions Domain Capabilities

### 1.1 Admission Offer Management
* **Owning Domain**: Admissions
* **Purpose**: Manages the issuance, validity, and status of admission offers made to applicants.
* **POC Requirement**: Required (to validate if the student has a valid offer to accept).
* **Execution**: Deterministic service (database lookup/validation).
* **Dependencies**: None.

### 1.2 Offer Acceptance
* **Owning Domain**: Admissions
* **Purpose**: Captures and records the student's intent to accept an offer.
* **POC Requirement**: Required.
* **Execution**: Agent-assisted or Deterministic service.
* **Dependencies**: None.

### 1.3 Admission Requirement Evaluation
* **Owning Domain**: Admissions
* **Purpose**: Determines what preconditions must be met before an accepted offer becomes a confirmed admission.
* **POC Requirement**: Required.
* **Execution**: Deterministic rules engine / Agent-evaluated.
* **Dependencies**: None.

### 1.4 Admission Payment Requirement Determination
* **Owning Domain**: Admissions
* **Purpose**: Specifically evaluates whether a financial deposit or payment is required to confirm the admission, and determines the amount.
* **POC Requirement**: Required.
* **Execution**: Deterministic rules engine.
* **Dependencies**: Passes requirement to Finance for execution.

### 1.5 Admission Confirmation
* **Owning Domain**: Admissions
* **Purpose**: Finalizes the admission state, transitioning the applicant to an "Admission Confirmed" status.
* **POC Requirement**: Required.
* **Execution**: Deterministic service.
* **Dependencies**: Requires successful result from Finance if payment was determined mandatory by 1.4.

---

## 2. Finance Domain Capabilities

### 2.1 Financial Obligation Management
* **Owning Domain**: Finance
* **Purpose**: Creates and tracks a formal financial obligation against a user based on a valid request.
* **POC Requirement**: Required.
* **Execution**: Deterministic service.
* **Dependencies**: Receives request from Admissions.

### 2.2 Payment Processing / Execution
* **Owning Domain**: Finance
* **Purpose**: Handles the actual execution of a payment transaction against an obligation.
* **POC Requirement**: Required (conceptually/mocked for POC).
* **Execution**: Deterministic integration / Workflow.
* **Dependencies**: None (internal to Finance).

### 2.3 Payment Status Management
* **Owning Domain**: Finance
* **Purpose**: Tracks and reports the real-time status of a payment (Pending, Success, Failed).
* **POC Requirement**: Required.
* **Execution**: Deterministic service.
* **Dependencies**: Status is returned to Admissions.

### 2.4 Financial Transaction Recording
* **Owning Domain**: Finance
* **Purpose**: Records the finalized successful transaction to the institutional ledger.
* **POC Requirement**: Required.
* **Execution**: Deterministic service.
* **Dependencies**: None.
