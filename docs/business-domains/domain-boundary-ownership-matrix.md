# Domain Boundary & Ownership Matrix

**Version:** 1.0  
**Status:** Pending Review  

This matrix establishes clear ownership boundaries and explicitly calls out what falls *outside* a domain's scope to prevent ambiguous overlap.

| Domain | Primary Responsibility | In Scope | Out of Scope | Primary Stakeholders | Related Domains |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admissions** | Prospective student journey | Campaigns, Applications, Evaluation, Offers, Admission Confirmation | Enrollment, Student Records, Fee Collection | Admissions Officers, Applicants | Student Lifecycle, Fees & Payments |
| **Student Lifecycle** | Student institutional journey and program standing | Enrollment, Program Changes, Withdrawals, Graduation Eligibility | Individual Course Registration, Grading, Alumni Engagement | Registrar, Students | Admissions, Academic Management, Alumni |
| **Academic Management** | Academic structure and delivery | Curriculum, Courses, Registration, Timetables, Grading, Exams | Program Enrollment, Faculty HR Lifecycle | Deans, Faculty, Students | Student Lifecycle, Faculty, Campus & Facilities |
| **Faculty** | Faculty academic responsibilities | Academic Profiles, Course Allocation, Workload, Availability | Payroll, General Employee Benefits, Hiring | Provost, Dept Heads, Faculty | Academic Management, Human Resources |
| **Research** | Institutional research activities | Grants, Publications, Patents, Research Projects | Academic Curriculum, Disbursing Funds | Researchers, Grant Agencies | Finance, Human Resources |
| **Human Resources** | Employee lifecycle | Hiring, Onboarding, Leave, Performance, Compensation Policy, Payroll Calculation | Payroll Execution (Disbursement), Vendor Payments | HR Staff, Employees | Finance, Faculty |
| **Career & Placement** | Employment opportunities | Job Postings, Placement Drives, Interviews, Offer Tracking | Academic Standing, Alumni Engagement | Placement Officers, Students | Student Lifecycle, Alumni |
| **Alumni** | Graduate relationship management | Alumni Engagement, Events, Mentorship, Donations | Graduation Eligibility, Student Records | Alumni Office, Graduates | Student Lifecycle, Finance |
| **Finance** | Institutional financial operations | Accounting, Budgets, Ledger, Payroll Execution, Expense Reporting | Student Fee Calculations, Procurement POs | CFO, Finance Team | HR, Procurement, Fees & Payments |
| **Fees & Payments** | User financial obligations | Fee Calculation, Invoicing, Payment Collection, Refunds | Ledger Maintenance, Scholarship Evaluation | Student Accounts, Students | Finance, Student Lifecycle |
| **Scholarships & Financial Aid** | Institutional financial assistance | Applications, Eligibility, Award Decisions, Renewals | Applying funds to Ledger (handled by Fees) | Financial Aid Office | Fees & Payments, Student Lifecycle |
| **Procurement & Vendor Management** | Purchasing and supply chain | Requisitions, POs, Vendor Onboarding, Inventory | Final Vendor Invoice Payment | Procurement, Depts | Finance, Campus & Facilities |
| **Campus & Facilities** | Physical environment | Buildings, Maintenance, Room Bookings, Utilities | Academic Timetable Generation | Facilities Team | Academic Management, Housing |
| **Housing / Hostel** | Student accommodation | Room Allocation, Check-in/out, Residential Incidents | Hostel Fee Invoicing, Building Maintenance | Housing Office, Students | Fees & Payments, Campus & Facilities |
| **Transportation** | Institutional transport | Routes, Vehicles, Passes, Schedules | Transport Fee Collection | Transport Office, Users | Fees & Payments |
| **Library** | Library resources | Catalogue, Borrowing, Digital Resources, Fines Assessment | Fine Payment Collection | Librarians, Users | Fees & Payments |
| **IT Services** | Technology provisioning and support | User Accounts, Devices, IT Incidents, Software | Platform Identity & Access Management core | IT Department, Users | All Domains |
| **Student Services** | General student requests layer | Case Management, Enquiry Routing, Certificates, Escalations | Executing underlying domain processes (e.g., Grading) | Student Success, Students | All Domains |
| **Student Activities** | Extracurricular engagement | Clubs, Events, Student Organizations | Academic Transcripts | Student Affairs | Student Services, Finance |
| **Institutional Analytics** | Reporting and decision support | Dashboards, KPI Tracking, Predictive Analytics | Domain-specific transactional reporting | Exec Leadership | All Domains |
| **Governance & Compliance** | Regulatory and policy framework | Audits, Policies, Accreditation, Risk Management | Operational execution of compliance rules | Compliance Officers | All Domains |

## Key Boundary Decisions

1. **HR vs. Finance (Payroll)**: 
   * **HR** owns compensation policy, salary configurations, timesheets, and payroll calculation (determining how much is owed).
   * **Finance** owns the financial execution, banking disbursements, and ledger posting.
2. **Admissions vs. Student Lifecycle**: 
   * The boundary is exactly at the point of the "Admission Confirmed" business event. Following this event, **Student Lifecycle** assumes ownership of the student record (Enrollment). (Specific requirements like initial deposits are Admissions business rules, not the domain boundary itself).
3. **Student Lifecycle vs. Academic Management**: 
   * **Student Lifecycle** owns macro-level progression (Program/Degree standing, overall graduation eligibility).
   * **Academic Management** owns micro-level progression (Course delivery, daily attendance, term grading).
   * *Note: Ambiguous areas like credit accumulation, failed/repeat courses, and transfer credits are recorded as future boundary/process questions to be resolved during the Business Capability design phase.*
4. **Student Services as an Orchestration Layer**:
   * **Student Services** acts as a facade. It tracks a student's request for a document, but relies on **Student Lifecycle** or **Academic Management** to actually generate or validate the document data.
