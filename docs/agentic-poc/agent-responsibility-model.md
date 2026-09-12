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
* **Prohibited Responsibilities**: Financial execution, ledger management, payment status determination.
* **Prohibited Actions**: Execute financial transactions, arbitrarily waive mandatory payments without configured policy authorization.
* **Delegation Rules**: MUST delegate any actual financial execution to the Finance Agent.
* **Escalation Rules**: Escalate to human review if Finance returns an unresolvable permanent failure, or if the offer is in an invalid/unknown state.

## 2. Finance Agent

* **Identity**: `agent.finance.primary`
* **Domain Affiliation**: Finance
* **Responsibility Scope**: Execute financial requests, process payments, and record transactions.
* **Authorized Decisions**: 
  * Validate request schema and authorization.
  * Evaluate idempotency rules (detect duplicates).
  * Determine appropriate payment workflow to invoke.
* **Authorized Actions**: 
  * Invoke Financial Obligation Management.
  * Invoke Payment Processing / Execution.
  * Invoke Financial Transaction Recording.
  * Return structured Financial Results.
* **Capabilities it may invoke**: Financial Obligation Management, Payment Execution, Transaction Recording.
* **Prohibited Responsibilities**: Admission decision logic, fee waiver logic.
* **Prohibited Actions**: Transition admission states, determine *why* a student is paying.
* **Delegation Rules**: Returns results back to the requesting agent rather than continuing their workflow.
* **Escalation Rules**: Escalate to human review for massive refunds, manual ledger adjustments, or if the underlying payment gateway is permanently offline.

*(Note: The structured payload definitions for Agent-to-Agent interaction have been moved to `agent-contracts.md`)*
