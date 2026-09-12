# Phase 3 Pre-Flight Boundary Analysis

## 1. Canonical Source Basis

According to the canonical `business-domain-catalogue.md` and `domain-boundary-ownership-matrix.md`:

**Finance Domain**
* Owns: Institutional financial operations, accounting, ledger, budgets, and payroll execution.
* Boundary Rule: "Does not manage individual student fee calculations (handled by Fees & Payments)."

**Fees & Payments Domain**
* Owns: User financial obligations, fee calculation, invoicing, payment collection, receipts, and refunds.

## 2. Current POC Responsibility

The current POC assigns the following responsibilities for the admission deposit payment to the **Finance Agent**:
* Financial obligation execution
* Payment processing/execution
* Payment transaction recording

The current flow is: Admissions Agent → Finance Agent → Admissions Agent.

## 3. Boundary Comparison

The current POC directly routes a student payment collection (the admission deposit) to the Finance domain. However, the canonical architecture explicitly assigns student invoicing and payment collection to the **Fees & Payments** domain. 

By having the Finance Agent execute the student payment processing, the POC is bypassing the Fees & Payments domain entirely, which violates the established canonical boundaries.

## 4. Decision

**BOUNDARY CORRECTION REQUIRED**

**Reasoning:** The agentic platform must accurately reflect the institutional business architecture. Encoding a direct Admissions → Finance student payment flow into the technical architecture would embed a structural contradiction. The POC must be corrected to use the Fees & Payments domain for student-facing financial obligations.

## 5. Recommended POC Flow

The POC must be updated to align with the canonical domain model:

```text
Student
  ↓
Admissions Agent
  ↓
Fees & Payments Agent
  ↓
Student Payment Collection (Deterministic Capability)
  ↓
Payment Confirmed (Business Event)
  ↓
Admissions Agent
  ↓
Admission Confirmed
```

*(Note: Fees & Payments will eventually reconcile with Finance for the institutional ledger, but Admissions does not interact with Finance directly for student payments).*

## 6. Impact Assessment

To implement this boundary correction, the following POC documents must be updated to replace the role of "Finance" with "Fees & Payments" regarding student payment collection:

* `docs/agentic-poc/README.md`
* `docs/agentic-poc/poc-scope.md`
* `docs/agentic-poc/business-capability-model.md`
* `docs/agentic-poc/business-process.md`
* `docs/agentic-poc/business-rules.md`
* `docs/agentic-poc/agent-responsibility-model.md`
* `docs/agentic-poc/agent-decision-execution-model.md`
* `docs/agentic-poc/agent-contracts.md`
* `docs/agentic-poc/open-questions.md`
