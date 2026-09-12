# ADR 011: POC Technology Stack

**Context:** We need to select the foundational technologies for the POC implementation phase.

**Decision:** We will use **Python, FastAPI, Pydantic, and SQLite**.

**Alternatives:**
* Node.js / Express / Zod (Considered: Valid, but Python currently has richer, more mature first-party LLM SDKs for building raw agent loops).
* PostgreSQL (Rejected: Requires external daemon setup; SQLite is simpler for local execution).

**Rationale:** 
* **Python**: Standard for AI development.
* **FastAPI**: Provides automatic OpenAPI schema generation and routing for the Agent-to-Agent REST contracts.
* **Pydantic**: Enforces strict payload validation at the boundary, throwing errors for malformed requests before the LLM sees them.
* **SQLite**: Perfect for local, isolated state stores (one file for Admissions, one for Fees & Payments).

**Consequences:** The POC will be easy to run locally without complex container orchestration, allowing engineers to focus on the agentic patterns rather than infrastructure.
