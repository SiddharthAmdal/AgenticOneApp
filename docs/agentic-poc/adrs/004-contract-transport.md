# ADR 004: Contract Transport & Serialization

**Context:** We must define how the Phase 2 agent contracts (`StudentPaymentRequest`, `StudentPaymentResult`) are physically validated and transported.

**Decision:** Contracts will be serialized as **JSON payloads** transported via HTTP POST, and validated using **Pydantic/JSON Schema** at the boundary of each agent runtime.

**Alternatives:**
* Protobuf (Rejected: Overkill, lacks human-readability for debugging).
* Open-ended LLM parsing (Rejected: Violates the requirement for deterministic, structured communication).

**Rationale:** JSON provides universal compatibility. Strong **structural validation** at the REST endpoint (via Pydantic) ensures the receiving agent (Fees & Payments) never processes a malformed request (missing fields, wrong types), throwing a Validation Failure before invoking the LLM. Any subsequent **business/authorization validation** is performed within the agent's logic.

**Consequences:** Both agents must implement strict API boundaries (e.g., FastAPI) that enforce the schema before passing the context into the agent reasoning loop.
