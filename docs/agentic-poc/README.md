# OneApp Agentic POC

**Phase:** POC Phase 2 — Minor Corrections Complete  
**Status:** Ready for Phase 3  

## POC Purpose
This Proof of Concept (POC) is designed to validate the **agentic operating model** of the OneApp platform. It is intended to demonstrate how autonomous agents can collaborate across established business domain boundaries to fulfill a single, cohesive user request while strictly preserving domain ownership and human accountability.

## Why Admissions + Finance?
This scenario was selected because it perfectly illustrates the boundary between business rules (determining *what* must happen) and operational execution (actually *doing* it). 
* **Admissions** owns the rules for whether a student must pay a deposit to confirm their admission.
* **Finance** owns the execution of that payment.
This prevents Admissions from creeping into financial operations and forces an explicit, structured agent-to-agent delegation.

## POC Business Scenario
> **A student accepts an admission offer and completes the required admission payment.**

## POC Success Outcome
> **Admission Confirmed** (The canonical business event signaling the end of the Admissions domain's responsibility).

## Domains Involved
1. **Admissions**
2. **Finance**

## Scope & Constraints
This POC is intentionally constrained to a single vertical slice. It does not replace the broader OneApp 21-domain business architecture. For explicit boundaries, see the [POC Scope](poc-scope.md) document.

## Relationship to the Canonical Business Domain Architecture
This POC relies completely upon the v1.0 Canonical Business Domain Architecture (`docs/business-domains/`). It does not modify, merge, or split any of the established 21 business domains. It merely implements a vertical slice through two of them.

## Expected Future Phases
1. **Initialization & Business Analysis (Complete)**
2. **Detailed Agent Responsibilities & Contracts (Complete)**
3. Technical Architecture & Tool Definitions
4. Orchestration Implementation
5. End-to-End Execution & Validation
