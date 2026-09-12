# Agent Decision & Execution Model

This document defines the conceptual lifecycle of an agent execution, distinguishing between agentic reasoning and deterministic capability execution. It establishes the pattern for how agents make decisions and initiate actions within the OneApp Agentic Platform.

## 1. Agent vs. Deterministic Capability Boundaries

**Principle:** Agents reason, coordinate, select authorized actions, and invoke capabilities. Deterministic services and workflows perform operations whose behavior should not depend on free-form LLM reasoning.

Agents do not act as the database, ledger, or payment gateway. They act as intelligent coordinators that delegate to established, predictable business capabilities.

## 2. Decision vs. Action

* **Agent Decision**: A determination made by the agent based on input, context, and rules (e.g., "A payment is required").
* **Agent Action**: The authorized operation the agent initiates as a result of a decision (e.g., "Invoke the 'Create Financial Action Request' capability").

**Conceptual Execution Flow:**
```text
INPUT → CONTEXT → EVALUATION/DECISION → AUTHORIZED ACTION → CAPABILITY INVOCATION → RESULT → NEXT DECISION/COMPLETION
```

## 3. The Conceptual Execution Lifecycle

### 3.1 Input
What enters the agent. Examples: User request, Agent-to-agent structured request, Business event, Workflow result.

### 3.2 Context
Information the agent considers. Examples: Business state (Offer status), Domain data, Applicable rules (ADM-R02), Authorized capabilities, Previous execution state.

### 3.3 Decision
What the agent determines. Examples: Intent, Relevant capability to invoke, Whether delegation is necessary, Whether execution may proceed.

### 3.4 Action
What the agent may do after deciding. Examples: Invoke a capability, Delegate to another agent, Emit a business event, Request human approval.

### 3.5 Outcome
The result of the action. Examples: Success, Business Failure (e.g., Payment Declined), Technical Failure, Pending state, Escalation.

## 4. Structured Decision Records

**Crucial Constraint:** The platform MUST NOT attempt to capture, store, expose, or depend upon the LLM's private chain-of-thought. 

Instead, agents must emit **Structured Decision Records** for auditability and operational understanding. A record contains:
* `DecisionID`: Unique identifier for the decision event.
* `AgentIdentity`: The agent making the decision.
* `Domain`: The owning business domain.
* `DecisionType`: (e.g., "PaymentRequirementEvaluation").
* `DecisionOutcome`: (e.g., "PaymentRequired").
* `ApplicableRules`: (e.g., ["ADM-R02"]).
* `RelevantState`: (e.g., {"OfferStatus": "Issued"}).
* `AuthorizedAction`: (e.g., "DelegateToFinance").
* `DelegationTarget`: (e.g., "agent.finance.primary").
* `CorrelationID`: The overarching workflow trace ID.

## 5. Agent Execution Flows

### 5.1 Admissions Agent Execution Trace
```text
User Request ("I accept my offer")
    ↓
[Admissions Agent]
    ↓
Decision: Understand Intent (Accept Offer)
Decision: Validate Offer (Valid)
Decision: Evaluate Rules (Deposit Required)
    ↓
Action: Delegate Financial Action Request
    ↓
(Handoff to Finance)
    ↓
Financial Result Received
    ↓
[Admissions Agent]
    ↓
Decision: Admission requirements are satisfied and payment has succeeded.
    ↓
Action: Invoke the deterministic Admission Confirmation capability.
    ↓
Execution: Deterministic capability performs the state transition.
    ↓
Outcome: Admission Confirmed
```

### 5.2 Finance Agent Execution Trace
```text
Financial Action Request (from Admissions)
    ↓
[Finance Agent]
    ↓
Decision: Validate Request Format (Valid)
Decision: Validate Authorization (Authorized)
Decision: Check Idempotency (New Request)
    ↓
Action: Invoke Financial Obligation Capability
Action: Invoke Payment Workflow
    ↓
[Deterministic Payment Workflow]
    ↓
Payment Result (Cleared)
    ↓
[Finance Agent]
    ↓
Action: Invoke Transaction Recording Capability
Action: Return Financial Result to Admissions
```

## 6. Traceability Model

To support future audit, debugging, and monitoring, the conceptual traceability model connects the entire flow without relying on opaque LLM logs:

```text
User Request ID
    ↓
Correlation ID (Ties the cross-domain workflow together)
    ↓
Structured Decision Record (Agent intent/rules applied)
    ↓
Agent Action (Authorized initiation)
    ↓
Idempotency Key (Protects specific capability execution)
    ↓
Capability Execution (Deterministic infrastructure logging)
    ↓
Business Event (Canonical state change)
    ↓
Final Outcome
```
