# Agent Capability Access Matrix

This matrix explicitly defines which agents are authorized to invoke which deterministic capabilities. It acts as a hard authorization boundary in the technical architecture.

| Agent | Capability | Allowed? | Reason |
| :--- | :--- | :--- | :--- |
| **Admissions Agent** | Admission Offer Management | **Yes** | Own domain responsibility |
| **Admissions Agent** | Payment Requirement Evaluation | **Yes** | Own domain business rules |
| **Admissions Agent** | Admission Confirmation | **Yes** | Own domain responsibility |
| **Admissions Agent** | Delegate Student Payment | **Yes** | Explicitly permitted cross-domain delegation |
| **Admissions Agent** | Payment Collection Execution | **No** | Fees & Payments owns collection execution |
| **Admissions Agent** | Student Receipt Generation | **No** | Fees & Payments owns financial receipting |
| **Fees & Payments Agent** | Student Payment Collection | **Yes** | Own domain responsibility |
| **Fees & Payments Agent** | Idempotency Validation | **Yes** | Own domain responsibility |
| **Fees & Payments Agent** | Receipt Generation | **Yes** | Own domain responsibility |
| **Fees & Payments Agent** | Validate Payment Request | **Yes** | Own domain boundary validation |
| **Fees & Payments Agent** | Admission Confirmation | **No** | Admissions owns student admission state |
| **Fees & Payments Agent** | Admission Offer Evaluation | **No** | Admissions owns offer logic |
| **Fees & Payments Agent** | Institutional Ledger Update | **No** | Finance owns the canonical ledger |
