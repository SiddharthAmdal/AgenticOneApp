# ADR 006: State Ownership

**Context:** Admissions and Fees & Payments both need to persist state (offers, obligations, receipts).

**Decision:** We will implement **Logically Segregated Data Stores** (e.g., separate SQLite databases or distinctly prefixed tables) for Admissions and Fees & Payments.

**Alternatives:**
* Single monolithic database without boundaries (Rejected: Violates domain ownership rules).
* Distributed Postgres clusters (Rejected: Unnecessary infrastructure overhead).

**Rationale:** We must demonstrate that agents cannot directly manipulate another domain's state. Physical or logical segregation of databases enforces this architecture. Admissions cannot `UPDATE fees_payments.obligations`.

**Consequences:** Operations involving both states (e.g., confirming admission based on payment) must rely exclusively on the structured Agent-to-Agent contracts, validating the business model.
