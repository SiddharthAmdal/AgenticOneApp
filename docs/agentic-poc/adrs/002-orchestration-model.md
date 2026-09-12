# ADR 002: Orchestration Model

**Context:** We must determine who owns the workflow progression for the Admission Confirmation process.

**Decision:** We will use **Admissions-Agent-Led Orchestration / Delegation**.

**Alternatives:**
* Central API Gateway / Orchestrator (Rejected: Removes business logic and flow control from the domain agent, turning it into a dummy responder).
* BPMN Workflow Engine (Rejected: Over-complicates the POC and shifts decision-making to the workflow engine rather than the agent).
* Event-Driven Choreography (Rejected: Business events are for observation, not workflow control. The Admissions Agent directly delegates to Fees & Payments via REST to retain workflow progression ownership).

**Rationale:** The canonical business model dictates that Admissions owns the admission process. Therefore, the Admissions Agent should start the flow, explicitly delegate the payment task to Fees & Payments, and resume when the result is returned. 
* **Domain-agent-led orchestration**: The Admissions Agent owns progression of the admission business process because Admissions owns the process.
* **Agent-to-agent delegation**: Admissions delegates the student payment operation to Fees & Payments because Fees & Payments owns that capability. 

**Consequences:** The Admissions Agent runtime must handle pausing/resuming or waiting synchronously for the Fees & Payments result.
