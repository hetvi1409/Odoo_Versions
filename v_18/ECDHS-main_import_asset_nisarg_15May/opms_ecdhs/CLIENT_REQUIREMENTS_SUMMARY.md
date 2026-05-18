# OPMS ECDHS Client Requirements Summary (One Page)

## Project Objective

Deliver a production-ready Organisational Performance Management System (OPMS) for the Eastern Cape Department of Human Settlements (ECDHS) to plan, capture, approve, and report KPI performance quarterly, with evidence-based accountability.

## Business Outcomes Required

1. Reliable departmental KPI tracking across Programme, Sub-Programme, and Directorate levels.
2. Standardized quarterly reporting for management and legislature submissions.
3. Clear accountability through auditable workflows and approvals.
4. Better decision-making via dashboards, status indicators, and trend views.

## Must-Have Functional Capabilities

### 1) KPI Planning and Performance Data
- KPI setup per directorate
- Annual target and Q1–Q4 planning
- APP/AOP indicator support

### 2) Workflow and Approvals
- Editor submission
- Director review and sign-off
- GM final approval
- Quarter lifecycle controls (open/close/lock)

### 3) Evidence and Compliance
- Evidence upload linked to KPI reports
- File validation and duplicate checks
- Full traceability and audit records

### 4) Dashboards and Reporting
- Traffic-light status (Red/Amber/Green)
- Submission and achievement visibility
- Pending approvals and leadership summaries

### 5) Portal Experience
- Role-based portal access
- KPI viewing, reporting, evidence upload
- Approval-status tracking for users

### 6) Security and Governance
- Role-based access control
- Organizationally scoped visibility
- Controlled admin/import permissions

### 7) Excel Import and Onboarding
- Bulk KPI import from `.xlsx`
- Required-column validation
- Create/Update/Skip import modes
- Hierarchy mapping/creation during import
- Import logs, history, and safe failure handling

## Non-Functional Expectations

1. **Data integrity:** no broken hierarchy/KPI relationships.
2. **Auditability:** approvals, imports, and evidence actions are traceable.
3. **Reliability:** controlled quarter windows and consistent import behavior.
4. **Usability:** clear messages, role-specific dashboards, efficient routine use.
5. **Security:** least-privilege access and protected evidence handling.

## Client Decisions Still Needed

1. Final hierarchy source of truth during import:
   - Spreadsheet Programme/Sub-Programme values, or
   - Directorate code-derived hierarchy.
2. Directorate naming normalization policy for inconsistent variants.
3. Cross-year duplicate strategy for similar KPI names.
4. Confirmation of mixed target format storage (number/date/text) approach.

## Delivery Acceptance Checklist

- KPI management, workflow, evidence, dashboards, and portal modules operational.
- Excel KPI import works with validation and history.
- Role permissions and organizational assignments enforced.
- Quarterly approval lifecycle executes end-to-end.
- Reporting outputs are usable for management and legislature-facing needs.
