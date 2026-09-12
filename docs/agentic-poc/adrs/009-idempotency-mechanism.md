# ADR 009: Idempotency Mechanism

**Context:** We must ensure that the same payment is not executed twice if a transient network failure causes the Admissions Agent to retry a request.

**Decision:** The **Fees & Payments Domain** will own and persist the `Idempotency Key` linked to the corresponding `Business Transaction ID` (Receipt) in its data store.

**Alternatives:**
* Admissions Agent maintains idempotency state (Rejected: Fails if Admissions crashes; idempotency must be protected at the execution boundary).
* Using the `Correlation ID` as the Idempotency Key (Rejected: Correlation ID represents the whole workflow, whereas we might need multiple distinct payment attempts).

**Rationale:** The exact principle is "One Idempotency Key -> One Logical State-Mutating Operation." When Fees & Payments receives a request, it checks its local store for the key. If it exists, it immediately returns the previously generated result without re-executing the payment capability.

**Consequences:** The Admissions agent is responsible for passing the same key on a retry, and a new key if a new distinct payment attempt is warranted. Fees & Payments must check this key transactionally before invoking the payment gateway mock.
