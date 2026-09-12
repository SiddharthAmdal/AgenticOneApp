# ADR 008: Business Events

**Context:** We need a way to emit and observe canonical business events (e.g., `Admission Confirmed`, `Payment Confirmed`).

**Decision:** We will use **Structured JSON Events written to an in-memory event bus or dedicated log file** to represent canonical state transitions.

**Alternatives:**
* Kafka / RabbitMQ (Rejected: Over-engineering for a local POC).
* Treating HTTP responses as events (Rejected: HTTP 200 is a technical event, not a durable record of a business state change).

**Rationale:** The POC must distinguish between technical handoffs (REST calls) and authoritative business state changes. Writing these distinct events to a mock event log demonstrates the architectural boundary clearly without heavy infrastructure. 

**Crucial Distinction:** 
* **REST request/response ≠ Business Event**
* **Business Event ≠ Workflow Control Signal**

The event mechanism is strictly for **Business Event Recording / Observation**, NOT **Event-Driven Workflow Orchestration**. The deterministic capability emits an authoritative business event when a state transition occurs (e.g., `Payment Confirmed`). These events are for observability and audit. They must NOT secretly become a second orchestration mechanism. The Admissions Agent determines the next step from the structured REST result it receives, not from the event bus.

**Consequences:** Deterministic capabilities must be instrumented to emit these business events upon successfully mutating domain state.
