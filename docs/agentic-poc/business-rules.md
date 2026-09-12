# POC Business Rules

This document inventories the business rules required for the POC, categorizing them by owning domain and verifying their status.

## 1. Admissions Rules

| Rule ID | Rule Description | Classification |
| :--- | :--- | :--- |
| **ADM-R01** | An offer may only be accepted if its status is exactly `Issued` and the expiration date has not passed. | Confirmed from existing architecture |
| **ADM-R02** | Payment requirements (whether required, and how much) are dictated by Admissions program configurations, not by Finance. | Confirmed from existing architecture |
| **ADM-R03** | If a payment is determined to be mandatory, the admission state cannot transition to `Admission Confirmed` until a successful result is received from Finance. | Confirmed from existing architecture |
| **ADM-R04** | If Finance returns a `Failed` result, the offer remains in the `Offer Accepted` (Pending Payment) state. | POC Assumption |
| **ADM-R05** | Admissions may not directly update the financial ledger or assume a payment was successful without Finance's explicit confirmation. | Confirmed from existing architecture |

## 2. Finance Rules

| Rule ID | Rule Description | Classification |
| :--- | :--- | :--- |
| **FIN-R01** | Finance will only create a payment obligation upon receiving a valid, structured request from an authorized domain (Admissions). | Confirmed from existing architecture |
| **FIN-R02** | A structured request must contain, at minimum: Requesting Domain, Student ID, Amount, Currency, Correlation ID, and an **Idempotency Key**. | POC Assumption |
| **FIN-R03** | **Idempotency Rule**: If Finance receives a request with an **Idempotency Key** that has already been processed, it must not process a duplicate payment. It must return the status of the existing transaction. | POC Assumption |
| **FIN-R04** | A payment is considered successful only when the transaction clears (mocked as immediate for this POC). | POC Assumption |
| **FIN-R05** | Finance does not determine *why* a payment is needed; it merely executes the requested financial action and returns the result. | Confirmed from existing architecture |

## 3. Failure & Retry Semantics

Failures must be explicitly classified to determine agent behavior:

* **Business Failure** (e.g., Payment Declined, Invalid Offer): The operation completed but business rules reject success. Agents handle this gracefully (e.g., notify user, keep state pending). Retry is usually not automatic unless user corrects details.
* **Validation Failure** (e.g., Malformed Contract, Unauthorized): The request was invalid. The caller (Admissions Agent) must not retry identical requests. Requires code/human review.
* **Transient Technical Failure** (e.g., Network Timeout, Gateway Unavailable): Infrastructure failed. The caller (Admissions) may safely retry the exact same request using the *same Idempotency Key*.
* **Permanent Technical Failure** (e.g., Database Corrupted): Cannot be retried safely. Requires human escalation.
