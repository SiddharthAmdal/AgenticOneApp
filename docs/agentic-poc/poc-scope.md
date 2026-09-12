# POC Scope

This document defines the exact boundaries of the Agentic Vertical Slice POC to ensure it remains a focused proof of the operating model rather than a sprawling implementation.

## In Scope
* Admission offer validation (checking if an offer exists and is valid).
* Offer acceptance processing (capturing student intent).
* Admission acceptance requirement evaluation.
* Payment/deposit requirement determination (evaluating Admissions business rules).
* Explicit financial execution request (Agent-to-Agent delegation).
* Structured financial result generation and handling.
* Admission confirmation state transition.
* Agent-to-agent structured delegation and contracts.
* Business-event and state transitions (e.g., Offer Accepted -> Admission Confirmed).
* Request correlation and traceability (at a conceptual, business level).
* Handling of primary success and failure scenarios (e.g., payment failure).

## Out of Scope
* Full, production-grade implementations of the Admissions or Fees & Payments domains.
* Real banking or payment gateway integrations (mocked execution will be used).
* The complete Student Lifecycle (the POC ends exactly at "Admission Confirmed").
* Enrollment implementation (owned by Student Lifecycle, out of scope here).
* Scholarships and Financial Aid evaluations.
* Complex fee structures, payment plans, or recurring billing.
* Complete Identity & Access architecture (SSO, RBAC).
* Production security architecture and hardening.
* Production-scale orchestration infrastructure (e.g., Kafka, Kubernetes).
* General-purpose autonomous agent behavior (agents will only perform defined business tasks).
* Any of the other 19 business domains defined in the canonical architecture.

*Note: The POC boundary is an artificial slice for validation purposes. It does not redefine the real business-domain boundaries established in the canonical architecture.*
