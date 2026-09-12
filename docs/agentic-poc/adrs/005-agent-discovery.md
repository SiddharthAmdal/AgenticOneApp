# ADR 005: Agent Discovery

**Context:** The Admissions Agent needs to know how to reach the Fees & Payments Agent.

**Decision:** We will use **Static Configuration (Environment Variables / Config Files)**.

**Alternatives:**
* Consul / Eureka Registry (Rejected: Introduces heavy infrastructure).
* Dynamic Agent Registry API (Rejected: Over-engineering for a 2-agent POC).

**Rationale:** The POC operates with known, fixed identities (`agent.admissions.primary` and `agent.fees-payments.primary`). Hardcoding their local host endpoints in configuration is the simplest, most effective approach.

**Consequences:** If we add more agents, the configuration file must be updated manually. This is acceptable for the POC.
