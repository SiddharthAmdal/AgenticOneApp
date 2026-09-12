# ADR 001: Agent Runtime Model

> [!WARNING]
> **Status: Superseded**
> **Superseded By: [ADR 012](012-langchain-langgraph-adoption.md)**
> *This document is preserved for historical record. The POC has since adopted LangGraph and LangChain.*

**Context:** We need to define how agents execute, evaluate context, and invoke capabilities in the POC without obscuring the decision-making process.

**Decision:** We will use a lightweight programmatic execution loop (custom agent runtime) that interacts directly with an LLM API, utilizing explicit tool/function calling for capabilities.

**Alternatives:** 
* LangChain / LangGraph (Rejected: Introduces too much abstraction, obscuring explicit traceability of the Decision -> Action loop).
* Temporal.io (Rejected: Overkill for POC, adds unnecessary infrastructure).

**Rationale:** A custom lightweight loop ensures we maintain strict control over emitting Structured Decision Records exactly when business decisions are made, avoiding hidden chain-of-thought execution inside a heavy framework.

**Consequences:** We must manually wire the tool-calling loop and error handling, but we gain total transparency into the agent's logic.
