# ADR 012: LangChain & LangGraph Adoption

**Context:** During the Phase 4 implementation kickoff, the decision was made to adopt standard agentic frameworks (LangChain and LangGraph) to implement the execution loops and model abstractions, reversing the initial decision to use purely custom runtime loops (see ADR 001).

**Decision:** We will implement the agent execution logic using **LangGraph** (for stateful execution and orchestration graphs) and **LangChain** (for LLM tool abstractions and structured interaction). The LLM provider will be **NVIDIA NIM** using the `openai/gpt-oss-20b` model.

**Alternatives:**
* **Custom Python Loops:** (Initially decided). While pure, standard frameworks provide better out-of-the-box state management, persistence checkpoints, and tool binding capabilities.
* **Other Agent Frameworks (e.g., AutoGen, CrewAI):** (Rejected). LangGraph offers explicit, graph-based control over workflow state which tightly aligns with our strict Admissions-led orchestration requirements.

**Rationale:**
* **Why LangGraph:** It provides a highly explicit, observable state-machine mechanism for executing the agent's workflow (e.g., Admissions Agent determining if payment is required -> delegating -> resuming). It maps perfectly to our domain-agent-led orchestration requirement.
* **Why LangChain:** It provides standardized model abstractions and tool binding. We use it to expose our deterministic capabilities as tools to the LLM without reinventing function-calling boilerplate.
* **Why GPT-OSS-20B via NVIDIA NIM:** To demonstrate compatibility with high-performance, open-source models deployed on dedicated endpoints, isolated behind our `xsc_lib_extn` adapter.

**Consequences (Architectural Invariants Preserved):**
* **Domain Ownership:** The use of LangGraph does NOT change business ownership. Admissions still owns the workflow; Fees & Payments still owns the payment capability.
* **Deterministic Boundaries:** LangChain tools are merely wrappers. The actual capability implementations remain strictly deterministic Python functions that execute SQL and emit Business Events. LLM outputs are never treated as authoritative state changes.
* **State Encapsulation:** LangGraph state (checkpointing) is treated purely as *execution state*. Authoritative business state remains in the isolated domain SQLite databases.
* **Provider Isolation:** NVIDIA NIM configuration is abstracted behind `xsc_lib_extn/llm/`, preventing domain modules from being coupled to a specific vendor SDK.
