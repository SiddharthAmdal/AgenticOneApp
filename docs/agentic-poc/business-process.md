# POC Business Process

**Process Name:** Admission Offer Acceptance & Payment  
**Participating Domains:** Admissions, Finance  
**Trigger:** Student initiates acceptance of an admission offer.  
**Preconditions:** Student exists, valid admission offer exists in "Issued" state.  

## Process Steps & Handoffs

| Step | Action | Owning Domain | Execution Type |
| :--- | :--- | :--- | :--- |
| **1** | Student requests to accept their offer. | Admissions | Agent-assisted |
| **2** | Validate the admission offer is active and valid. | Admissions | Deterministic service |
| **3** | Transition offer state to *Offer Accepted*. | Admissions | Deterministic service |
| **4** | Determine if a payment/deposit is required, and the amount. | Admissions | Deterministic rules engine |
| **5** | **[CROSS-DOMAIN HANDOFF]** Generate structured *Financial Action Request* and delegate to Finance. | Admissions → Finance | Agent-executed delegation |
| **6** | Receive request, validate idempotency, and create financial obligation. | Finance | Agent-executed / Deterministic |
| **7** | Execute payment processing (mocked for POC). | Finance | Workflow |
| **8** | Record transaction success/failure. | Finance | Deterministic service |
| **9** | **[CROSS-DOMAIN HANDOFF]** Return structured *Financial Result* to Admissions. | Finance → Admissions | Agent-executed return |
| **10** | Evaluate financial result. If successful, fulfill payment requirement. | Admissions | Agent-executed |
| **11** | Transition state to *Admission Confirmed*. | Admissions | Deterministic service |
| **12** | Notify student of successful confirmation. | Admissions | Agent-assisted |

## Business Events & State Transitions

1. **Offer Accepted**: Triggered at Step 3. (State: `Offer Issued` -> `Offer Accepted`)
2. **Financial Action Requested**: Triggered at Step 5.
3. **Payment Confirmed**: Triggered at Step 8 if successful.
4. **Payment Failed**: Triggered at Step 8 if the payment is declined or fails business rules.
5. **Admission Confirmed**: Triggered at Step 11. (State: `Offer Accepted` -> `Admission Confirmed`)

## Outcomes

* **Success Outcome**: The student's state is strictly transitioned to `Admission Confirmed` and Finance has recorded the payment transaction.
* **Failure Outcomes**: 
  * If the offer is invalid, process terminates at Step 2.
  * If Finance reports payment failure at Step 9, Admissions evaluates the failure, notifies the student, and leaves the state at `Offer Accepted` (Pending Payment). 

## Postconditions
The applicant is ready for handoff to the **Student Lifecycle** domain for Enrollment, representing the hard boundary established in the canonical architecture.
