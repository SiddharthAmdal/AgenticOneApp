# Agent Responsibility Model

This document translates the business model into explicit agent responsibilities. It ensures that agents act strictly within their authorized domain boundaries.

## 1. Admissions Agent

* **Identity**: `agent.admissions.primary`
* **Domain Affiliation**: Admissions
* **Responsibility Scope**: Manage the applicant journey from offer issuance through to Admission Confirmed.
* **Authorized Decisions**: 
  * Determine user intent regarding offer acceptance.
  * Evaluate offer validity.
  * Determine if payment is required (and amount) based on domain rules.
  * Determine if financial result satisfies the admission requirement.
* **Authorized Actions**: 
  * Transition offer state to Accepted.
  * Delegate financial execution to Finance.
  * Invoke the deterministic Admission Confirmation capability.
* **Capabilities it may invoke**: Admission Offer Management, Offer Acceptance, Requirement Evaluation, Admission Confirmation.
* **Prohibited Responsibilities**: Financial execution, student payment collection, payment status determination.
* **Prohibited Actions**: Execute financial transactions, collect payments, arbitrarily waive mandatory payments without configured policy authorization.
* **Delegation Rules**: MUST delegate any actual student payment execution to the Fees & Payments Agent.
* **Escalation Rules**: Escalate to human review if Fees & Payments returns an unresolvable permanent failure, or if the offer is in an invalid/unknown state.

## 2. Fees & Payments Agent

* **Identity**: `agent.fees-payments.primary`
* **Domain Affiliation**: Fees & Payments
* **Responsibility Scope**: Owns student financial obligation handling, validates payment requests, manages payment collection, invokes deterministic payment capabilities, determines/returns payment status, and handles receipt/reconciliation responsibilities within its domain.
* **Authorized Decisions**: 
  * Validate request schema and authorization.
  * Evaluate idempotency rules (detect duplicates).
  * Determine appropriate payment collection workflow to invoke.
* **Authorized Actions**: 
  * Invoke Student Financial Obligation Management.
  * Invoke Payment Collection / Payment Gateway Execution.
  * Invoke Receipting / Reconciliation.
  * Return structured Student Payment Results.
* **Capabilities it may invoke**: Student Financial Obligation Management, Payment Collection, Payment Status Management, Receipting / Reconciliation.
* **Prohibited Responsibilities**: Admission decision logic, determining admission eligibility, transitioning admission states, maintaining the institutional Finance ledger.
* **Prohibited Actions**: Transition admission states, determine *why* a student is paying, post directly to the institutional ledger.
* **Delegation Rules**: Returns results back to the requesting agent rather than continuing their workflow.
* **Escalation Rules**: Escalate to human review for manual payment corrections, refunds, or if the underlying payment gateway is permanently offline.

*(Note: The Finance Agent is downstream for institutional ledger reconciliation and is not an active participant in this admission-payment POC. The structured payload definitions for Agent-to-Agent interaction are located in `agent-contracts.md`)*
