# Business Domain Context Map

**Version:** 1.0  
**Status:** Pending Review  

This document visually represents the logical grouping of business domains and the key relationships and information flows between them.

## Domain Categorization

```mermaid
mindmap
  root((OneApp))
    Academic
      Admissions
      Student Lifecycle
      Academic Management
      Faculty
      Research
    People
      Human Resources
      Career & Placement
      Alumni
    Finance
      Finance
      Fees & Payments
      Scholarships & Financial Aid
      Procurement & Vendor Management
    Campus
      Campus & Facilities
      Housing / Hostel
      Transportation
      Library
      IT Services
    Student Experience
      Student Services
      Student Activities
    Institutional
      Institutional Analytics
      Governance & Compliance
```

## Key Cross-Domain Relationships

### 1. The Student Academic Journey
This represents the canonical flow of a student through the primary academic domains.

```mermaid
flowchart TD
    A[Admissions] -->|Admission Confirmed Event| SL[Student Lifecycle]
    SL -->|Program Enrollment| AM[Academic Management]
    AM -->|Course Completion & Grades| SL
    SL -->|Graduation / Completion| AL[Alumni]
    SL -->|Academic Standing| CP[Career & Placement]
```

### 2. The Student Financial Lifecycle
This highlights how student financial obligations interact with academic and funding domains.

```mermaid
flowchart LR
    SL[Student Lifecycle] -->|Enrollment Changes| FP[Fees & Payments]
    AM[Academic Management] -->|Course Registrations| FP
    H[Housing / Hostel] -->|Room Charges| FP
    L[Library] -->|Fines| FP
    SFA[Scholarships & Financial Aid] -->|Awards / Credits| FP
    FP -->|Ledger Reconciliation| F[Finance]
```

### 3. The Institutional Resource Flow
This demonstrates how HR, Finance, and Faculty domains interact regarding staff and resources.

```mermaid
flowchart TD
    HR[Human Resources] <-->|Payroll Calc / Financial Execution| F[Finance]
    F <-->|Vendor Payments| PVM[Procurement & Vendor Management]
    HR -->|Employee Profile| FAC[Faculty]
    FAC -->|Teaching Availability| AM[Academic Management]
    CF[Campus & Facilities] -->|Space Availability| AM
    CF -->|Housing Infrastructure| H[Housing / Hostel]
```

### 4. The Student Service Layer
This highlights the role of Student Services as an orchestration and routing layer.

```mermaid
flowchart TD
    S([Student]) <--> SS[Student Services Layer]
    SS -.->|Routes Transcripts| SL[Student Lifecycle]
    SS -.->|Routes Fee Queries| FP[Fees & Payments]
    SS -.->|Routes IT Issues| IT[IT Services]
    SS -.->|Routes Maintenance| CF[Campus & Facilities]
```

## Platform Layer Dependency
All domains implicitly rely on the Cross-Cutting Platform Capabilities (Identity, Workflow, Policy, Documents, Notifications, Search, Audit, Agent Orchestration). They are not shown as domains above to maintain architectural clarity.
