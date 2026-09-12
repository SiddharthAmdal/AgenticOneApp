# OneApp Business Domains

**Version:** 1.0  
**Status:** Pending Review  

## Overview
This directory contains the canonical **Business Domain documentation** for the OneApp Agentic Platform. 

OneApp is an institutional platform designed around clearly bounded business domains. As part of our transition toward an agentic architecture, we define the business architecture first. Only after domains, capabilities, and processes are established do we introduce AI agents to handle specialized operations.

## Principles
1. **Business ownership comes first**: Every capability has a clear business owner.
2. **Avoid unnecessary fragmentation**: Domains represent meaningful business ownership and lifecycle boundaries.
3. **Avoid overlapping ownership**: Explicit boundaries exist between domains (e.g., HR vs. Finance for payroll).
4. **Distinguish domains from platform services**: Business domains handle business operations; shared platform services (Identity, Workflow, Notifications) are cross-cutting capabilities.
5. **Agents come later**: We do not prematurely turn every domain into an LLM agent.
6. **Preserve human accountability**: AI does not automatically own authoritative institutional decision-making.

## Documentation Structure
- [Business Domain Catalogue](business-domain-catalogue.md): Comprehensive definitions of each domain, purpose, and responsibilities.
- [Business Domain Context Map](business-domain-context-map.md): Visual and logical representation of domains and their relationships.
- [Domain Boundary & Ownership Matrix](domain-boundary-ownership-matrix.md): Clear definition of what is in and out of scope for each domain.
- [Domain Capability Map](domain-capability-map.md): High-level business capabilities assigned to each domain.

## Cross-Cutting Platform Capabilities
The following are implemented as shared platform services and consumed by business domains, rather than being treated as independent business domains:
* Identity & Access
* Workflow
* Policy / Rules
* Documents
* Notifications
* Search / Knowledge
* Audit
* Agent Orchestration
