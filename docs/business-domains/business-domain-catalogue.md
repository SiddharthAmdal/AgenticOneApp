# Business Domain Catalogue

**Version:** 1.0  
**Status:** Pending Review  

## Document Purpose
This document defines the major business areas (domains) within OneApp. It outlines the purpose, responsibilities, and primary stakeholders for each domain, distinguishing them from cross-cutting platform capabilities.

## Architectural Context
The OneApp platform relies on business domains as the highest level of organization. A domain is a logical boundary that encapsulates related business capabilities, data, and processes.

## Domain Classification

### 1. Academic
#### 1.1 Admissions
* **Purpose**: Manages the prospective student journey from lead generation and application through to the final admission decision.
* **Primary Responsibilities**: Admission campaigns, applicant profiles, eligibility checks, document verification, evaluation, merit/ranking, offers, and admission confirmation.
* **Boundary**: Concludes at the "Admission Confirmed" business event, at which point ownership hands over to the Student Lifecycle domain. (Payment of deposits or specific prerequisites are treated as Admissions business rules, not hard architectural boundaries).
* **Stakeholders**: Admissions Officers, Prospective Students, Academic Evaluators.

#### 1.2 Student Lifecycle
* **Purpose**: Manages the student's institutional journey from initial enrollment to graduation and alumni transition.
* **Primary Responsibilities**: Enrollment, onboarding, student records, program enrollment, transfers, leave of absence, withdrawals, suspension, graduation eligibility, and alumni transition.
* **Boundary**: Owns program-level progression and lifecycle status, not individual course registrations (handled by Academic Management).
* **Stakeholders**: Registrar, Students, Academic Advisors.

#### 1.3 Academic Management
* **Purpose**: Manages the academic structure, curriculum delivery, and course-level student progression.
* **Primary Responsibilities**: Programs, curriculum, courses, prerequisites, course registration, attendance, assessment, grading, examinations, timetables, and academic scheduling.
* **Boundary**: Owns the delivery of education. Consumes faculty availability from the Faculty domain.
* **Stakeholders**: Deans, Department Heads, Faculty, Students.

#### 1.4 Faculty
* **Purpose**: Manages faculty members in their academic and teaching capacities.
* **Primary Responsibilities**: Faculty academic profiles, onboarding (academic), department assignment, course allocation, teaching workload, availability, and academic performance inputs.
* **Boundary**: Owns academic responsibilities. Employment and payroll aspects remain with HR and Finance.
* **Stakeholders**: Faculty, Department Heads, Provost.

#### 1.5 Research
* **Purpose**: Manages institutional research activities, funding, and outputs.
* **Primary Responsibilities**: Research projects, publications, grants, patents, collaborations, and research compliance.
* **Boundary**: Distinct from academic teaching. Funding disbursements coordinate with Finance.
* **Stakeholders**: Researchers, Research Administration, Grant Agencies.

---

### 2. People
#### 2.1 Human Resources
* **Purpose**: Manages the complete lifecycle of all institutional employees (staff and faculty).
* **Primary Responsibilities**: Workforce planning, recruitment, employee records, leave, attendance, transfers, promotions, compensation policy, payroll calculation, performance management, and offboarding.
* **Boundary**: HR owns compensation policy and calculation. Finance owns financial execution and disbursement.
* **Stakeholders**: HR Staff, Employees, Managers.

#### 2.2 Career & Placement
* **Purpose**: Connects students and recent graduates with employment and internship opportunities.
* **Primary Responsibilities**: Employer management, job postings, placement drives, interview scheduling, offer tracking, and career profiles.
* **Boundary**: Relies on Student Lifecycle for student academic standing and eligibility.
* **Stakeholders**: Placement Officers, Students, Employers.

#### 2.3 Alumni
* **Purpose**: Manages the institution's ongoing relationship with its graduates.
* **Primary Responsibilities**: Alumni profiles, engagement, events, networking, mentorship, and donations.
* **Boundary**: Assumes ownership of the student profile after the Student Lifecycle domain processes graduation.
* **Stakeholders**: Alumni Relations Office, Alumni.

---

### 3. Finance
#### 3.1 Finance
* **Purpose**: Manages core institutional financial operations, accounting, and controls.
* **Primary Responsibilities**: Budgets, accounting, expenses, revenue, financial approvals, financial reporting, and payroll execution/disbursement.
* **Boundary**: Handles the institution's ledger. Does not manage individual student fee calculations (handled by Fees & Payments).
* **Stakeholders**: CFO, Finance Team, Auditors.

#### 3.2 Fees & Payments
* **Purpose**: Manages financial obligations and transactions for students and other service users.
* **Primary Responsibilities**: Fee structures, calculations, student invoices, payment collection, receipts, outstanding dues, refunds, and payment plans.
* **Boundary**: Interfaces with Student Lifecycle for enrollment changes and Finance for ledger reconciliation.
* **Stakeholders**: Student Accounts, Students, Parents/Sponsors.

#### 3.3 Scholarships & Financial Aid
* **Purpose**: Manages institutional financial assistance programs.
* **Primary Responsibilities**: Scholarship programs, eligibility, applications, evaluation, award decisions, and renewals.
* **Boundary**: Awards result in credits applied to student accounts in the Fees & Payments domain.
* **Stakeholders**: Financial Aid Office, Students, Sponsors.

#### 3.4 Procurement & Vendor Management
* **Purpose**: Manages institutional purchasing, supply chain, and external vendors.
* **Primary Responsibilities**: Vendor onboarding, purchase requisitions, purchase orders, receiving, and inventory management.
* **Boundary**: Procurement handles the purchasing process; Finance handles the actual vendor invoice payment.
* **Stakeholders**: Procurement Team, Department Heads, Vendors.

---

### 4. Campus
#### 4.1 Campus & Facilities
* **Purpose**: Manages the institution's physical infrastructure and spaces.
* **Primary Responsibilities**: Buildings, rooms, facility bookings, maintenance, work orders, utilities, and space allocation.
* **Boundary**: Provides spaces used by Academic Management (timetables) and Housing.
* **Stakeholders**: Facilities Management, Staff, Students.

#### 4.2 Housing / Hostel
* **Purpose**: Manages student residential accommodations.
* **Primary Responsibilities**: Housing applications, room allocation, check-in/out, and residential incidents.
* **Boundary**: Fees generated here are processed by Fees & Payments.
* **Stakeholders**: Housing Office, Resident Students, Wardens.

#### 4.3 Transportation
* **Purpose**: Manages institutional transportation and fleet services.
* **Primary Responsibilities**: Routes, vehicles, drivers, schedules, transport passes, and vehicle maintenance.
* **Boundary**: Fees for transport passes integrate with Fees & Payments.
* **Stakeholders**: Transport Office, Students, Staff.

#### 4.4 Library
* **Purpose**: Manages library resources, circulation, and digital catalogues.
* **Primary Responsibilities**: Catalogue, borrowing, returns, fines, digital resources.
* **Boundary**: Fines generated integrate with Fees & Payments.
* **Stakeholders**: Librarians, Students, Faculty.

#### 4.5 IT Services
* **Purpose**: Manages institutional technology services, hardware, and access.
* **Primary Responsibilities**: User accounts, devices, software provisioning, IT incidents, service requests.
* **Boundary**: Operates as a domain for IT operations, separate from the underlying Identity & Access platform capability.
* **Stakeholders**: IT Department, All Users.

---

### 5. Student Experience
#### 5.1 Student Services
* **Purpose**: Acts primarily as a service-entry / routing / case-orchestration layer for student requests.
* **Primary Responsibilities**: General enquiries, service requests, certificates, letters, case management, and status tracking.
* **Boundary**: Does not own or execute the underlying business processes (e.g., grading, fee calculation, IT operations, facilities maintenance). It routes requests to the responsible domain and tracks fulfillment.
* **Stakeholders**: Student Success Team, Students.

#### 5.2 Student Activities
* **Purpose**: Manages extracurricular activities, student life, and community engagement.
* **Primary Responsibilities**: Clubs, societies, events, competitions, student leadership, and activity records.
* **Boundary**: Distinct from academic records.
* **Stakeholders**: Student Affairs, Student Leaders.

---

### 6. Institutional
#### 6.1 Institutional Analytics
* **Purpose**: Provides centralized reporting, BI, and decision-support for the institution.
* **Primary Responsibilities**: Dashboards, KPI tracking, operational/predictive analytics, and management reporting.
* **Boundary**: Consumes data from all domains to provide cross-domain insights.
* **Stakeholders**: Executive Leadership, Domain Managers.

#### 6.2 Governance & Compliance
* **Purpose**: Manages regulatory compliance, risk, and institutional policies.
* **Primary Responsibilities**: Policies, accreditation, regulatory reporting, internal controls, risk management, and audits.
* **Boundary**: Defines compliance requirements that other domains must execute within their workflows.
* **Stakeholders**: Compliance Officers, Legal, Executive Leadership.

---

## Assumptions & Open Questions
1. **Assumption**: Procurement & Vendor Management has been added as a new domain under Finance/Operations, as vendor purchasing is a distinct business capability from ledger accounting.
2. **Assumption**: Payroll calculation is assigned to HR, while payroll financial execution/disbursement is assigned to Finance.
3. **Open Question**: Does Global Mobility / Study Abroad warrant a separate domain, or is it a sub-capability within Student Lifecycle?
4. **Open Question**: Should Health & Wellness (Clinic/Counseling) be added as a distinct domain under Student Experience?
