# OneApp Agentic POC

**Phase:** POC Phase 3 — Technical Architecture & Tool Definitions Complete  
**Status:** Ready for Architecture Review  

## POC Purpose
This Proof of Concept (POC) is designed to validate the **agentic operating model** of the OneApp platform. It is intended to demonstrate how autonomous agents can collaborate across established business domain boundaries to fulfill a single, cohesive user request while strictly preserving domain ownership and human accountability.

## Why Admissions + Fees & Payments?
This scenario was selected because it perfectly illustrates the boundary between business rules (determining *what* must happen) and operational execution (actually *doing* it). 
* **Admissions** owns the rules for whether a student must pay a deposit to confirm their admission.
* **Fees & Payments** owns the execution of that student payment collection.
This prevents Admissions from creeping into financial operations and forces an explicit, structured agent-to-agent delegation.

## POC Business Scenario
> **A student accepts an admission offer and completes the required admission payment.**

## POC Success Outcome
> **Admission Confirmed** (The canonical business event signaling the end of the Admissions domain's responsibility).

## Domains Involved
1. **Admissions**
2. **Fees & Payments**

*(Note: Finance is downstream for institutional ledger reconciliation and is not in the active synchronous POC execution path).*

## Scope & Constraints
This POC is intentionally constrained to a single vertical slice. It does not replace the broader OneApp 21-domain business architecture. For explicit boundaries, see the [POC Scope](poc-scope.md) document.

## Relationship to the Canonical Business Domain Architecture
This POC relies completely upon the v1.0 Canonical Business Domain Architecture (`docs/business-domains/`). It does not modify, merge, or split any of the established 21 business domains. It merely implements a vertical slice through two of them.

## Expected Future Phases
1. **Initialization & Business Analysis (Complete)**
2. **Detailed Agent Responsibilities & Contracts (Complete)**
3. **Technical Architecture & Tool Definitions (Complete)**
4. Orchestration Implementation
5. End-to-End Execution & Validation

*The primary cross-domain interaction demonstrated is:*
`Admissions Agent` → `Fees & Payments Agent` → `Student Payment Result` → `Admissions Agent`
