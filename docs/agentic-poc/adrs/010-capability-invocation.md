# ADR 010: Capability Invocation Model

**Context:** Agents must invoke deterministic operations without manipulating underlying databases directly.

**Decision:** Agents will invoke capabilities using **Local Function/Tool Calling** which internally wrap deterministic service interfaces (methods).

**Alternatives:**
* Direct SQL Execution by Agent (Rejected: Violates domain encapsulation and determinism).
* Executing external microservices via HTTP for every capability (Rejected: For capabilities within the agent's own domain, local function calls are sufficient and simpler for the POC).

**Rationale:** Providing strict tool schemas (e.g., `confirm_admission(student_id)`) forces the LLM to output structured parameters. The underlying Python/Node function executes the deterministic logic (validation, DB write, event emission) protecting the authoritative state.

**Consequences:** We must implement strict parameter validation inside the deterministic capability functions before any state is mutated.
