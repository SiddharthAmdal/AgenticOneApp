# Open Architectural Questions & Validation

This document captures unresolved architectural questions that must be addressed in the technical implementation phases. It also provides the validation matrix ensuring the POC adheres to the canonical Business Domain v1.0 baseline.

## 1. Architecture Questions to Capture

These questions represent concrete technical architecture decisions that must be addressed in the Technical Architecture phase:

* **Orchestration / Topology**: Is there a central request/orchestration component (e.g., a routing API gateway), or do agents communicate directly peer-to-peer?
* **Discovery**: How does the Admissions agent technically discover the endpoint/address of the Fees & Payments agent?
* **Communication Protocol**: Is agent-to-agent communication synchronous (REST/gRPC/MCP) or asynchronous (Message Broker/Event Bus like Kafka/RabbitMQ)?
* **Contract Serialization & Versioning**: How are the structured JSON contracts physically validated and versioned at runtime?
* **Identity & Security**: How is agent identity technically established and authorized? (e.g., mTLS, JWTs, API Keys).
* **State Management**: Where does the business state physically live? (e.g., Domain-specific Postgres databases).
* **Decision Record Storage**: Where and how are the Structured Decision Records stored for auditability?
* **Business Events Infrastructure**: How are business events (like `Admission Confirmed`) published to the wider platform?
* **Failure Handling UX**: How are asynchronous technical failures propagated back to the user interface?
* **Agent Runtime**: What specific framework (if any) hosts the agents (e.g., LangChain, custom loop, temporal.io)?
* **Deterministic Execution**: How do agents physically invoke deterministic capabilities (e.g., HTTP APIs, local function calling)?

---

## 2. Architectural Validation Matrix

This matrix validates the POC against the existing Canonical Business Domain Architecture.

| Principle | Validation Conclusion |
| :--- | :--- |
| **Admissions owns admission decisions** | Validated. Admissions handles all offer logic and transitions the state to Admission Confirmed. |
| **Fees & Payments owns student payment collection** | Validated. Fees & Payments manages the student financial obligation and collection. |
| **Payment requirements remain Admissions rules** | Validated. Admissions evaluates ADM-R02 to determine if payment is required before making the request. |
| **Domain boundaries are preserved** | Validated. The POC respects canonical boundaries, cleanly handing off payment to Fees & Payments. |
| **Agents do not replace business ownership** | Validated. Agents act strictly within the capabilities and rules assigned to their domain. |
| **Cross-domain communication occurs through explicit responsibility** | Validated. The Agent-to-Agent interaction is a structured, explicit delegation contract, not open-ended conversation. |
| **Human accountability is preserved** | Validated. Agents cannot override institutional policies like waiving mandatory fees or issuing massive refunds. |
| **Business events are distinguished from technical events** | Validated. "Admission Confirmed" is treated as a canonical business event, distinct from a technical HTTP success response. |
| **POC scope does not redesign the 21-domain baseline** | Validated. The POC merely implements a vertical slice through 2 of the 21 existing domains. |
