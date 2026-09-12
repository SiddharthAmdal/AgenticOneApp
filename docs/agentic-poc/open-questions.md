# Open Architectural Questions & Validation

This document captures unresolved architectural questions that must be addressed in the technical implementation phases. It also provides the validation matrix ensuring the POC adheres to the canonical Business Domain v1.0 baseline.

## 1. Resolved in Phase 3 (Technical Architecture)

These architectural decisions have been resolved and documented in the ADRs and `technical-architecture.md`:

* **Orchestration / Topology**: Resolved as Admissions-Agent-Led Orchestration / Delegation.
* **Discovery**: Resolved as Static Configuration (Environment Variables).
* **Communication Protocol**: Resolved as Synchronous HTTP/REST.
* **Contract Serialization & Versioning**: Resolved as JSON payloads over HTTP POST validated by Pydantic.
* **Identity & Security**: Resolved via explicit Domain/Agent identifiers in payloads; implicit trust for POC.
* **State Management**: Resolved as isolated domain-specific SQLite databases.
* **Decision Record Storage**: Resolved as JSON logs sent to a mock observability aggregator.
* **Business Events Infrastructure**: Resolved as structured JSON logs emitted by deterministic capabilities.
* **Failure Handling UX**: Resolved.
* **Agent Runtime**: Resolved as a custom, lightweight Python execution loop wrapping LLM SDKs.
* **Deterministic Execution**: Resolved as Local Function Calling (Tools) wrapping internal service methods.

## 2. Deferred to Future Implementation / Production Architecture
*(None currently recorded. Complex production IAM, Kafka eventing, and Kubernetes deployments are intentionally excluded from the POC scope).*

---

## 3. Architectural Validation Matrix

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
