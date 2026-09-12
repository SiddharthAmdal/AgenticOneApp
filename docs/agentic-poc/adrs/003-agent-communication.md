# ADR 003: Agent Communication Model

**Context:** The Admissions Agent must communicate with the Fees & Payments Agent to request payment collection.

**Decision:** We will use **Synchronous HTTP/REST** for inter-agent communication.

**Alternatives:**
* Kafka / RabbitMQ Asynchronous Events (Rejected: Introduces unnecessary infrastructure complexity for a localized POC).
* gRPC (Rejected: Harder to debug and inspect payloads locally compared to REST).

**Rationale:** Prioritizing simplicity, explicit contract enforcement, and ease of testing. Synchronous HTTP provides immediate success/failure responses, making the agent delegation loop straightforward to implement and debug.

**Consequences:** The Admissions Agent will block (or await) while the Fees & Payments Agent processes the request. We must simulate transient HTTP timeouts to demonstrate the retry and idempotency logic.
