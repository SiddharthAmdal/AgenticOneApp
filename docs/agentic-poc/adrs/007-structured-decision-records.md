# ADR 007: Structured Decision Records

**Context:** The platform must record agent decisions without relying on unstructured LLM chain-of-thought traces.

**Decision:** We will serialize **Structured Decision Records** as structured JSON logs written to standard output / log files (or a mock observability backend) at the exact moment the agent commits to a decision and selects an action.

**Alternatives:**
* Storing traces directly in the domain database (Rejected: Pollutes domain state with operational agent metadata).
* Extracting intent post-facto from LLM API logs (Rejected: Violates the requirement to avoid chain-of-thought dependency).

**Rationale:** Emitting JSON logs containing the `DecisionID`, `CorrelationID`, `DecisionType`, and `AuthorizedAction` ensures that an auditor can fully trace the agent's logic pathway using standard log aggregation tools, satisfying the auditability requirement.

**Consequences:** The agent runtime loop must explicitly demand structured output from the LLM that conforms to the Decision Record schema, and handle emitting it before executing the action.
