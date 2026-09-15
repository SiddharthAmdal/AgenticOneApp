---
Document: PROJECT_IMPLEMENTATION_BIBLE.md
Version: 2.0
Status: Review
Authority: Project Evolution / Historical Rationale / Change Governance
Last Updated: 2026-09-12
Current Phase: Phase 4 (Implementation)
Last Major Change: Expanded historical decision/change tracking and governance rules.
---

# PROJECT IMPLEMENTATION BIBLE
**OneApp Agentic Platform**

**Source of Truth Definition:** 
The Implementation Bible is the canonical source of truth for project evolution, historical rationale, decision chronology, architectural change history, and change governance. Individual canonical project documents (e.g., Business Rules, Technical Architecture, ADRs) remain authoritative for their respective subjects. 

---

## BIBLE CHANGE HISTORY

| Version | Date | Change | Reason | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | 2026-09-12 | Initial Bible created | Establish institutional project history | Superseded |
| 2.0 | 2026-09-12 | Expanded historical decision/change tracking | Improve completeness and governance | Review |

---

## EXECUTIVE SUMMARY

**What is OneApp?**
OneApp is a modular, agentic platform modeled around 21 distinct higher-education business domains. It replaces legacy monolithic orchestration with autonomous, domain-specific AI agents that collaborate to execute business processes.

**What are we proving with the POC?**
The POC demonstrates a cross-domain vertical slice: a student accepting an admission offer and completing a mandatory payment. It proves that autonomous domain agents can interact via explicit contracts to achieve an end-to-end business outcome without a central workflow engine, while preserving strict domain state boundaries.

**What is the current architecture?**
The architecture relies on **Admissions-Agent-Led Orchestration / Delegation**. 
- The **Admissions Agent** receives the request (routed by the Entry API), evaluates it, and delegates payment collection to the **Fees & Payments Agent** via synchronous HTTP REST.
- Agents use **LangGraph** for execution state and **LangChain** for LLM tool binding. 
- Authoritative state mutation is performed exclusively by **Deterministic Capabilities**, never directly by the LLM.

**Why is this architecture structured this way?**
To strictly enforce business domain boundaries. Orchestration is owned by the domain that owns the business process (Admissions). State is owned by the domain that generates it. This prevents the "distributed monolith" anti-pattern.

**What technologies are being used?**
- **Python, FastAPI, Pydantic** for contracts and REST boundaries.
- **LangGraph & LangChain** for agent execution and abstractions.
- **NVIDIA NIM (`openai/gpt-oss-20b`)** as the LLM provider.
- **SQLite** for isolated, domain-owned persistence.

**What are the biggest known limitations?**
- The `NVIDIA_NIM_API_KEY` is currently missing, blocking live smoke tests.
- Payments are mocked rather than using a real gateway (POC simplification).
- Security, authentication, and deployment infrastructure are intentionally simplified for the POC.

---

## 1. WHY THE PROJECT EXISTS

Higher-education systems often suffer from monolithic architectures where business rules are entangled across modules. The OneApp Agentic Platform exists to decouple these systems by aligning technical architecture precisely with business boundaries. By employing agentic AI, the platform allows autonomous domain experts (Agents) to negotiate and execute complex cross-domain workflows deterministically and auditably, avoiding brittle central orchestrators.

---

## 2. DOCUMENTATION AUTHORITY MAP

```text
PROJECT_IMPLEMENTATION_BIBLE.md (Authoritative for Project Evolution & Governance)
    │
    ├── Business Architecture (Authoritative for business definitions)
    │   ├── Business Domain Catalogue
    │   ├── Context Map
    │   ├── Boundary Ownership Matrix
    │   └── Capability Map
    │
    ├── POC Definition (Authoritative for POC boundaries)
    │   ├── POC Scope
    │   ├── Business Process
    │   ├── Business Rules
    │   └── Agent Responsibility Model
    │
    ├── Agent Architecture (Authoritative for agent execution rules)
    │   ├── Decision / Execution Model
    │   └── Agent Contracts
    │
    ├── Technical Architecture (Authoritative for current topology)
    │   ├── Technical Architecture
    │   ├── Tool Definitions
    │   └── Capability Access Matrix
    │
    └── ADRs (Authoritative for specific architectural decisions)
```

---

## 3. PROJECT EVOLUTION TIMELINE

1. **Business Domain Architecture**: 21-Domain Model established.
2. **Initial POC Proposal**: Admissions + Finance selected.
3. **Domain Boundary Review**: Discovered Finance does not collect student fees.
4. **POC Correction**: Scope realigned to Admissions + Fees & Payments.
5. **Agent Responsibility Model**: Defined agent vs. deterministic capabilities.
6. **Decision / Execution Model**: Structured Decision Records and Business Events defined.
7. **Agent Contracts**: JSON + Pydantic contracts designed.
8. **Technical Architecture**: Synchronous REST, isolated SQLite stores defined.
9. **Orchestration Refinement**: "Choreography" clarified to Admissions-Agent-Led Delegation.
10. **Initial Runtime Decision**: Custom lightweight Python runtime selected (ADR 001).
11. **Technology Reassessment**: Need for robust industry-standard state management.
12. **LangGraph + LangChain**: Adopted for execution state and LLM abstraction (ADR 012).
13. **Phase 4 Implementation Kickoff**: Code scaffolding and integration initiated.
14. **Phase 4.1 Skeleton**: Repository package structure and Entry API skeleton implemented.
15. **Phase 4.2 Common Infrastructure**: Centralized logger, exceptions, configuration, and gitignore implemented.
16. **Phase 4.3 Domain Models + Persistence**: Logically isolated SQLite repositories and domain models implemented for Admissions and Fees & Payments.
17. **Phase 4.4 Inter-Domain Contracts**: JSON/Pydantic validation models established for StudentPaymentRequest and StudentPaymentResult.
18. **Phase 4.5 Deterministic Business Capabilities**: Implemented canonical business rules and state transitions strictly decoupled from agent/LLM logic.
19. **Phase 4.6 LLM Provider Adapter**: Implemented an isolated, generic `NIMAdapter` interface configured for NVIDIA NIM (`openai/gpt-oss-20b`). Maps provider-specific structs to clean Pydantic domain models without leaking SDK dependencies or credentials. Live validation was successfully performed to confirm end-to-end provider connectivity.
20. **Phase 4.7 LangChain Tool Layer**: Designed LangChain wrapper tools linking agentic functions tightly and safely to existing Phase 4.5 capabilities. Authorized access matrices explicitly restrict `Admissions` and `Fees & Payments` tools, preserving firm architectural boundaries.
21. **Phase 4.8 LangGraph Agent Workflows**: Implemented decoupled LangGraph domain agents (`AdmissionsAgent` & `FeesPaymentsAgent`) configured with specialized system prompts and strict tool boundary enforcement. Integrated bounded state loops without executing arbitrary code. Inter-domain delegation remains cleanly stubbed behind tool abstractions (pending HTTP/REST). Tested exclusively against mocked Provider capabilities, isolating network and probabilistic variances.
22. **Phase 4.9 REST Boundaries & Entry API**: Implemented isolated FastAPI routers for Entry API (`/api/v1/entry`), Admissions Agent (`/api/v1/internal/admissions`), and Fees & Payments Agent (`/api/v1/internal/fees-payments`). Enforced strict Pydantic contract validation at HTTP boundaries using canonical `StudentPaymentRequest` and `StudentPaymentResult`. Validated caller identity structurally without introducing production IAM. Designed safe mapping of business rules and deterministic agent exceptions to appropriate HTTP status codes (400, 422, 500) without exposing internal stacks or chain-of-thought traces. Explicitly deferred actual cross-domain HTTP delegation logic to Phase 4.10.
23. **Phase 4.10 Agent Delegation**: Implemented a real synchronous REST-based agent delegation path from Admissions to Fees & Payments using `httpx`. Replaced the stubbed `DelegateStudentPaymentTool` with the `FeesPaymentsClient` abstraction that serializes `StudentPaymentRequest`, propagates `CorrelationID` inherently from `AdmissionsAgentState` (via `run_manager.metadata`), sets identity headers, and deserializes `StudentPaymentResult`. Distinctly separated business domain outcomes (e.g. `PaymentStatus=Declined`) from HTTP/transport infrastructure errors, bubbling transport exceptions as structured `DelegationError` mapped gracefully into the agent's context without polluting DB state or orchestration logic. Tested rigorously with `httpx.MockTransport`.
24. **Phase 4.11 Development-Only Reasoning Trace**: Implemented a constrained, isolated mechanism to capture the LLM's raw chain-of-thought (CoT) solely for forensic diagnostic purposes. The `NIMAdapter` was updated to intercept reasoning patterns (like `<think>` tags or `reasoning_content` extra fields) and funnel them into a `DevelopmentTracer` writing to an isolated local JSONL file (`data/dev_traces/reasoning_traces.jsonl`). The traces are correlated via `CorrelationID` and `DecisionID` where available, but never surface through APIs, `StudentPaymentResult`, canonical SDRs, or production logging facilities.

---

## 4. PHASE HISTORY

### Phase 0: Business Architecture
- **Objective:** Define the business domain decomposition.
- **Starting Assumptions:** Monolithic systems fail to scale.
- **Important Decisions:** Establishment of the 21-domain model and explicit boundary ownership.

### Phase 1: POC Definition
- **Objective:** Select a vertical slice to prove the agentic model.
- **Changes/Decisions:** Initially selected Admissions + Finance. Corrected to Admissions + Fees & Payments.

### Phase 2: Agent Model & Contracts
- **Objective:** Define how agents reason, execute, and communicate.
- **Important Decisions:** Separation of Decision (Agent) vs. Action (Deterministic Capability). Definition of JSON/Pydantic contracts.

### Phase 3: Technical Architecture
- **Objective:** Define runtime, infrastructure, and orchestration.
- **Important Decisions:** Admissions-Agent-Led Orchestration via synchronous REST. Custom lightweight runtime loop proposed (later superseded). Idempotency boundaries defined.

### Phase 4: Implementation
- **Objective:** Build the working POC using modern agentic frameworks.
- **Important Decisions:** Replaced the custom runtime with LangGraph and LangChain. Selected NVIDIA NIM and `gpt-oss-20b`.

---

## 5. DECISION LEDGER

| Decision ID | Phase | Category | Subject | Original Position | Final Decision | Reason | Supersedes | Status | Source |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| DEC-001 | 1 | POC Scope | Initial POC Slice | Admissions + Finance | Admissions + Fees & Payments | Canonical boundary rules dictate Finance does not collect student fees. | - | Active | POC Scope Docs |
| DEC-002 | 3 | Agent Architecture | Orchestration | Central Orchestrator / Choreography | Admissions-Agent-Led | Admissions owns the admission process lifecycle. Central orchestrators strip logic from domains. | - | Active | ADR 002 |
| DEC-003 | 3 | Technical Architecture | Communication | Unknown | Synchronous HTTP/REST | Avoids complex event-driven workflow control and maintains explicit caller logic. | - | Active | ADR 003, 004 |
| DEC-004 | 3 | Observability | Decision Auditing | Raw chain-of-thought logging | Structured Decision Records (SDR) | Model internals are not authoritative or stable. Need predictable audit logs. | - | Active | ADR 007 |
| DEC-005 | 3 | Observability | Business Events | Workflow controllers | Observation/Audit only | Using events for workflow control creates fragile implicit coupling. | - | Active | ADR 008 |
| DEC-006 | 3 | Implementation | Agent Runtime | Custom Python Loop | LangGraph + LangChain | Needed robust execution state management and standardized tool abstractions for the POC. | DEC-006a | Active | ADR 012 |
| DEC-006a| 3 | Implementation | Agent Runtime | Custom Python Loop | Custom Python Loop | Initial belief that frameworks obscured the Decision -> Action loop. | - | Superseded | ADR 001 |
| DEC-007 | 3 | Business Architecture | Idempotency | Undefined | Owned by Fees & Payments | The executing domain must protect its authoritative state from duplicate mutations. | - | Active | ADR 009 |
| DEC-008 | 3 | Implementation | LLM Provider | Undefined | NVIDIA NIM (`gpt-oss-20b`) | To demonstrate integration with an open-source model isolated via an adapter. | - | Active | Phase 4 Plan |

---

## 6. CHANGE LEDGER

| Change ID | Phase | Category | Before | After | Reason | Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CHG-001 | 2 | Business | POC: Admissions + Finance | POC: Admissions + Fees & Payments | Boundary correction. Finance is institutional ledger, not student collection. | Complete redirection of payment delegation. |
| CHG-002 | 3 | Agent | Ambiguous "Choreography" | Admissions-Agent-Led Delegation | Terminology caused confusion with event-driven message buses. | Explicitly defined that Admissions delegates via REST. |
| CHG-003 | 3 | Technical | `issue_payment_result` as LLM tool | `issue_payment_result` as runtime operation | Prevented LLM from hallucinating output formats. | Cleaner tool boundary. |
| CHG-004 | 4 | Implementation | Custom Python execution loop | LangGraph + LangChain | Adopted industry-standard execution state management for the POC. | ADR 012 created, ADR 001 updated. |
| CHG-005 | 3 | Technical | Structural validation inside Agent | Pydantic validation at HTTP boundary | Agents should not process malformed JSON; fail fast at REST boundary. | ADR 004 updated. |

---

## 7. REJECTED / SUPERSEDED APPROACHES

**1. Central Orchestration / BPMN Gateway**
- **Category:** Orchestration
- **Status:** Rejected Permanently
- **Why Rejected:** Strips business logic from the domain agent, turning it into a dummy responder. Violates the principle that domains own their processes.

**2. Event-Driven Choreography (Kafka/RabbitMQ)**
- **Category:** Communication
- **Status:** Rejected for current POC
- **Why Rejected:** Over-complicates the POC and makes execution flow implicit. We use synchronous REST for explicit workflow progression. Future production iterations may adopt this, but not for workflow control.

**3. Direct Agent State Mutation (LLM directly writing SQL)**
- **Category:** Agent Architecture
- **Status:** Rejected Permanently
- **Why Rejected:** LLM output is non-deterministic and cannot be trusted as an authoritative state transition. It must invoke deterministic capabilities instead.

**4. Recording Raw Chain-of-Thought as Authoritative**
- **Category:** Observability
- **Status:** Rejected Permanently for Production Audit
- **Why Rejected:** Model internals are not authoritative or stable. We require structured, predictable Structured Decision Records (SDRs) for auditing.
- **POC Exception (Phase 4.11):** A strictly isolated, development-only forensic reasoning trace is captured to a local JSONL sink for diagnostic/research correlation, but it is explicitly supplementary and never treated as proof of the model's actual causal reasoning.

**5. Custom Programmatic Python Loop**
- **Category:** Implementation
- **Status:** Superseded
- **Originally Considered Because:** Fear of frameworks obscuring the Decision->Action loop.
- **Why Rejected:** LangGraph provides superior execution state management without violating domain ownership.

---

## 8. HISTORICAL ARCHITECTURE vs CURRENT CANONICAL ARCHITECTURE

**Historical Architecture (What we used to believe):**
- The POC flow was Admissions -> Finance -> Admissions.
- Orchestration was vaguely defined as "Choreography" which implied event-driven execution.
- The agent runtime was a custom while-loop in pure Python to maintain strict control.
- `issue_payment_result` was exposed to the LLM to format the response.

**Current Canonical Architecture (What is currently approved):**
- The POC flow is Admissions -> Fees & Payments -> Admissions.
- Orchestration is strictly Admissions-Agent-Led via synchronous REST calls.
- The agent runtime uses LangGraph for stateful execution and LangChain for LLM abstractions.
- `issue_payment_result` is a backend transport operation.

---

## 9. CURRENT CANONICAL ARCHITECTURE

### Business Architecture
The platform is decomposed into 21 canonical domains. 
- **Admissions** owns the prospective student journey.
- **Fees & Payments** owns student financial obligations.
- **Finance** is EXCLUDED from the active synchronous POC (owns institutional ledgers).

### POC Architecture Flow
```text
Student
  ↓
OneApp Entry API (Composition Root / Router)
  ↓
Admissions Agent (LangGraph Workflow)
  ↓
Admissions Capabilities
  ↓
Fees & Payments Agent (LangGraph Workflow)
  ↓
Fees & Payments Capabilities
  ↓
Student Payment Result
  ↓
Admissions Agent
  ↓
Deterministic Admission Confirmation
  ↓
Admission Confirmed
```

### Agent Architecture
- **LangGraph:** Drives the state machine for each agent. (Execution State)
- **LangChain:** Provides LLM integration and tool abstraction.
- **Deterministic Capabilities:** Standard Python functions that interact with the database. The LLM only *requests* their execution.

### Data Architecture & Persistence
- **Isolated State:** SQLite databases per domain (`admissions.db`, `fees_payments.db`).
- **Idempotency:** Driven by `IdempotencyKey` stored in Fees & Payments.

### Observability
- **Structured Decision Records (SDR):** Canonical business/audit representation of the agent's decision outcome.
- **Business Events:** Emitted strictly after deterministic mutations for audit trails.
- **Development Reasoning Trace:** A non-authoritative, strictly isolated diagnostic JSONL sink capturing raw chain-of-thought (CoT) for forensic correlation. Never exposed to end users or ordinary application logs.

---

## 10. ARCHITECTURAL RATIONALE ("WHY IT IS THIS WAY")

- **Why Admissions owns orchestration:** (Business Reason) Admissions legally and operationally owns the admission lifecycle process.
- **Why Fees & Payments owns student payment collection:** (Business Reason) It specializes in student financial obligations, unlike Finance which handles B2B ledgers and payroll.
- **Why Finance is outside the active POC:** (POC Reason) Including downstream ledger reconciliation synchronous to admission acceptance is unnecessary and violates bounded contexts.
- **Why agents cannot directly mutate authoritative state:** (Technical Reason) LLMs are probabilistic. Databases require deterministic integrity.
- **Why LangGraph is used:** (Implementation Reason) Provides a standardized state-machine for agent execution pausing, resuming, and retry management.
- **Why LangChain is used:** (Implementation Reason) Reusable abstractions for binding Python functions as LLM tools.
- **Why synchronous REST is used:** (Technical Reason) Explicitly preserves the workflow control path in the caller (Admissions), preventing implicit event-driven spaghetti logic.
- **Why SQLite is used:** (POC Reason) Zero-configuration, local isolated state perfectly suited for proving domain encapsulation on a single developer machine.
- **Why business events are observation-only:** (Technical Reason) Using events as workflow control triggers creates brittle, hard-to-trace distributed monoliths.
- **Why Structured Decision Records exist:** (Business Reason) Auditing requires knowing exactly what business inputs led to an action, distinct from transient LLM "thinking".
- **Why the Entry API is not a business orchestrator:** (Business Reason) Central orchestration inevitably sucks business logic out of domains, recreating the monolith.

---

## 11. END-TO-END EXECUTION STORY

1. **User request:** Student submits "Accept Offer" to the Entry API.
2. **Entry API:** Generates `UserRequestID` and routes to Admissions Agent.
3. **Admissions Agent:** Invokes `get_admission_offer`. Evaluates status.
4. **Admissions Agent:** Invokes `evaluate_admission_requirements`. Determines payment is required.
5. **Payment delegation:** Agent invokes `delegate_student_payment`. Generates `CorrelationID` and `IdempotencyKey`.
6. **HTTP REST Call:** `StudentPaymentRequest` sent to Fees & Payments endpoint.
7. **Fees & Payments Validation:** Pydantic structurally validates request. Agent business validates it.
8. **Idempotency Check:** Agent invokes `collect_student_payment`. Capability checks `IdempotencyKey` in DB.
9. **Financial Obligation:** Capability creates obligation and executes mocked payment.
10. **Receipt/Business Transaction:** Capability generates `ReceiptID` and emits Business Event.
11. **StudentPaymentResult:** Returned to Admissions Agent.
12. **Admissions evaluation:** Agent sees Success.
13. **Admission confirmation:** Agent invokes `confirm_admission`. Capability mutates state and emits event.
14. **Final response:** Entry API returns success to user.

*(Failure Path - Duplicate Payment):* Fees & Payments capability detects existing `IdempotencyKey`. Immediately returns historical success without duplicate charge.
*(Failure Path - Timeout):* Admissions Agent experiences HTTP timeout. Retries exact same request with same `IdempotencyKey`.

---

## 12. CONTRACT AND IDENTITY MAP

| Identity | Purpose | Created By | Owned By | Passed To | Lifecycle | Retry Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **User Request ID** | Tracks the UI session. | Entry API | Entry API | All domains | Lives for duration of HTTP session. | Remains same across retries. |
| **Correlation ID** | Tracks cross-domain trace. | Calling Agent | Caller | Receiving Agent | Lives across network boundary. | May generate new span on retry. |
| **Idempotency Key** | Prevents duplicate mutation. | Admissions | Fees & Payments | Fees & Payments | Persisted in receiver DB permanently. | **MUST** remain identical on retry. |
| **Business Transaction ID** | Authoritative committed action (e.g. ReceiptID). | Capability | Capability | Caller | Permanent business record. | Returned identically on retry. |

*(Note: User Request ID and Correlation ID are technical tracing identifiers. Idempotency Key and Business Transaction ID are business identifiers).*

---

## 13. AGENT RESPONSIBILITY MAP

### Admissions Agent
- **Domain:** Admissions
- **Purpose:** Execute the admission confirmation lifecycle.
- **Responsibilities:** Evaluates offers, evaluates requirements, delegates payment, confirms admission.
- **Owned State:** `Offer`, `AdmissionStatus`
- **Allowed Capabilities:** `get_admission_offer`, `evaluate_admission_requirements`, `delegate_student_payment`, `confirm_admission`.
- **Prohibited Actions:** Collecting payments, writing to Fees & Payments DB.
- **Delegation Targets:** Fees & Payments.

### Fees & Payments Agent
- **Domain:** Fees & Payments
- **Purpose:** Securely execute student financial obligations.
- **Responsibilities:** Validates payment context, enforces idempotency, executes payment.
- **Owned State:** `FinancialObligation`, `Receipt`, `IdempotencyKey`
- **Allowed Capabilities:** `validate_payment_request`, `collect_student_payment`.
- **Prohibited Actions:** Confirming admission, determining *why* a payment is needed.
- **Delegation Targets:** None in POC.

---

## 14. NON-NEGOTIABLE ARCHITECTURAL INVARIANTS

1. **Domain ownership takes precedence over technical convenience.**
2. **Agents decide, deterministic capabilities act.**
3. **Agents cannot directly mutate authoritative domain state (No direct SQL).**
4. **Agents cannot directly write another domain's database.**
5. **Cross-domain interaction occurs through explicit API contracts.**
6. **Admissions cannot assume payment success without Fees & Payments confirmation.**
7. **Fees & Payments owns student payment collection; Finance does not.**
8. **Business events do not control POC workflow.**
9. **Execution state (LangGraph checkpoints) is not authoritative business state.**
10. **Idempotency must survive technical retries (Admissions must reuse the same key).**
11. **Private chain-of-thought must not be persisted as an observability artifact.**
12. **Technology changes must not silently alter business ownership.**
13. **Entry API must not become a hidden business orchestrator.**

---

## 15. IMPLEMENTATION STATUS MATRIX

| Component | Designed | Implemented | Tested | Verified | Baselined | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **21-Domain Architecture** | Yes | No | No | No | Yes | Domain Docs |
| **Admissions + F&P POC Flow** | Yes | No | No | No | Yes | Tech Architecture Docs |
| **Agent Contracts (JSON)** | Yes | Yes | Yes | No | Yes | Implementation (Phase 4.4) |
| **Deterministic Business Capabilities** | Yes | Yes | No | No | No | Implementation (Phase 4.5) |
| **LLM Provider Adapter** | Yes | Yes | Yes | No | No | Implementation (Phase 4.6) |
| **LangChain Tool Layer** | Yes | Yes | No | No | No | Implementation (Phase 4.7) |
| **LangGraph Workflows** | Yes | Yes | No | No | No | Implementation (Phase 4.8) |
| **Entry API Skeleton** | Yes | Yes | Yes | No | No | Implementation (Phase 4.9) |
| **Agent Delegation** | Yes | Yes | Yes | No | No | Implementation (Phase 4.10) |
| **Dev Reasoning Trace** | Yes | Yes | Yes | No | No | Implementation (Phase 4.11) |
| **Common Infrastructure** | Yes | Yes | No | No | No | Implementation (Phase 4.2) |
| **LangGraph Workflows** | Yes | No | No | No | No | Phase 4 Plan (ADR 012) |
| **SQLite Persistence** | Yes | Yes | No | No | Yes | Implementation (Phase 4.3) |

*(Note: Phase 4 Implementation has just kicked off. The repository currently contains no application code).*

---

## 16. CURRENT TECHNOLOGY STACK

| Technology | Purpose | Current Use | Why Selected | Alternatives | POC-Specific? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Python** | Core Language | Agent logic | Native AI SDK support | Node.js | No | Selected |
| **FastAPI** | REST API | Contracts | Automatic OpenAPI validation | Flask/Django | No | Selected |
| **Pydantic** | Validation | HTTP boundary | Strict typing | Marshmallow | No | Selected |
| **LangGraph** | Orchestration | Agent state | Explicit state machines | Custom Python Loop | No | Selected |
| **LangChain** | Abstraction | Tool binding | Standardized tool schemas | Raw API calls | No | Selected |
| **NVIDIA NIM** | LLM Provider | Engine | High-performance open-source | OpenAI/Anthropic | Yes | Selected (API Key missing, blocking live smoke test) |
| **SQLite** | Persistence | DB | Zero config local isolation | PostgreSQL | Yes | Selected |

---

## 17. POC LIMITATIONS vs ARCHITECTURAL CONCERNS

**Intentional POC Simplifications:**
- Mocked payment gateway.
- Local SQLite instead of distributed databases.
- Implicit trust between domain agents (No mTLS/JWT implemented).
- Static agent discovery instead of dynamic service mesh.
- Simplified deployment (no Docker/K8s setup).

**Open Architectural Concerns (Requiring future design):**
- **Saga/Compensating Transactions:** How to handle rollbacks if Admissions fails *after* Fees & Payments succeeds.
- **Production Data Seeding:** How test fixtures will be securely managed.

---

## 18. OPEN QUESTIONS / FUTURE DECISIONS

- **Question:** How do we handle production LLM rate limits and costs?
  - **Why it matters:** Agentic loops can consume massive token counts during retries.
  - **Current position:** POC uses a free/shared NVIDIA NIM endpoint.
  - **Decision required:** Production deployment requires dedicated provisioned throughput.
- **Question:** NVIDIA NIM API Key Missing.
  - **Why it matters:** Blocks the Phase 4 smoke test.
  - **Decision required:** Provide key via environment variable.

---

## 19. HOW FUTURE CHANGES MUST BE RECORDED

Future agents and engineers **MUST NOT** silently modify architecture. 

**Required Change Governance Process:**
1. **Classify Change:** Is it Business, Domain, Agent, Technical, or Implementation?
2. **Identify Affected Canonical Documents.**
3. **Determine ADR Requirement:** An ADR is REQUIRED for changes to domain boundaries, orchestration, communication, persistence, state ownership, security, and major framework changes.
4. **Draft ADR:** Document Previous State, Proposed State, Reason, Alternatives, and Impact.
5. **Approve / Baseline.**
6. **Implement & Test.**
7. **Update Implementation Bible:** Update the Decision Ledger and Change Ledger.
8. **Commit.**

---

## 20. CANONICAL SNAPSHOT

*(Authoritative only for the current state)*

- **Project:** OneApp Agentic Platform
- **Current POC:** Admissions + Fees & Payments
- **Orchestration Owner:** Admissions Agent
- **Agent Framework:** LangGraph
- **LLM Abstraction:** LangChain
- **Model Provider:** NVIDIA NIM
- **Initial Model:** `openai/gpt-oss-20b`
- **API:** FastAPI
- **Inter-Agent Communication:** Synchronous HTTP/REST
- **Contract Format:** JSON + Pydantic
- **Persistence:** Domain-owned SQLite stores
- **Authoritative State Mutation:** Deterministic capabilities
- **Decision Observability:** Structured Decision Records
- **Business Events:** Observation / audit only
- **Payment Idempotency Owner:** Fees & Payments
- **Finance:** Outside active synchronous POC
- **Entry API:** Composition/root API, not business orchestrator

*End of Document*
