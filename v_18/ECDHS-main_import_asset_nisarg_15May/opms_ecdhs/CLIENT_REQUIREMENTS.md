# OPMS ECDHS Client Requirements

## 1. Purpose

This document captures the client requirements for the OPMS ECDHS project, based on project overview, design, and implementation documents in the repository.

Client: Eastern Cape Department of Human Settlements (ECDHS)
System: Organisational Performance Management System (OPMS)

---

## 2. Functional Requirements

### 2.1 KPI and Performance Planning

The system shall:

1. Maintain organizational hierarchy levels for performance planning:
   - Programme
   - Sub-Programme
   - Directorate
2. Manage KPI definitions per directorate.
3. Capture annual targets and quarterly planned targets (Q1, Q2, Q3, Q4).
4. Support both APP and AOP indicator types.
5. Support annual and quarterly performance reporting cycles.

### 2.2 Reporting Workflow and Approvals

The system shall:

1. Support role-based reporting workflow:
   - Editor captures and submits reports
   - Director reviews and signs off
   - GM performs final approval
2. Enforce sequential approval states (no skipping workflow stages).
3. Track quarter states (open, closing, closed, locked) and enforce submission windows.
4. Record approval history, comments, and timestamps for accountability.

### 2.3 Evidence Management

The system shall:

1. Allow users to upload supporting evidence linked to KPI reports.
2. Validate evidence according to configured file constraints (including PDF validation where applicable).
3. Detect and prevent duplicate evidence/records where applicable.
4. Maintain evidence traceability and auditability.

### 2.4 Dashboards and Analytics

The system shall:

1. Provide management dashboards with KPI status and performance summaries.
2. Provide traffic-light performance indicators:
   - Red (not compliant/incomplete)
   - Amber (partially complete/in review)
   - Green (complete/approved)
3. Show submission rates, achievement trends, and pending approvals.
4. Support report outputs suitable for leadership and legislature reporting.

### 2.5 Portal Access and Self-Service

The system shall:

1. Provide portal access for authorized users.
2. Allow portal users (by role) to:
   - View KPIs and targets
   - Submit performance reports
   - Upload/view evidence
   - Track approval status
3. Support self-registration and admin approval for external/portal users.

### 2.6 Security and Access Control

The system shall:

1. Enforce role-based access control for all modules and actions.
2. Restrict data visibility by organizational assignment (programme/sub-programme/directorate).
3. Provide administrative user and assignment management.
4. Restrict import capabilities to authorized administrative roles.

### 2.7 Excel Import and Data Onboarding

The system shall:

1. Import KPI data from `.xlsx` files for financial years.
2. Validate required columns before import.
3. Support import modes:
   - Create new
   - Update existing
   - Skip existing
4. Automatically create or map organizational hierarchy from spreadsheet data (or configured mappings).
5. Create and link imported entities consistently:
   - Programme/Sub-Programme/Directorate
   - KPI
   - Annual Plan
   - Quarterly Targets
6. Maintain import history, logs, and recoverable error feedback.
7. Ensure import transactions are safe/atomic for critical failures.

---

## 3. Non-Functional Requirements

### 3.1 Data Integrity and Auditability

1. All workflow actions and approvals shall be traceable.
2. Data relationships shall preserve hierarchy and KPI lineage.
3. Import and evidence operations shall keep verifiable logs.

### 3.2 Usability

1. Users shall have role-appropriate dashboards and guided navigation.
2. Validation and error messages shall be clear and actionable.
3. Portal and backend flows shall support routine quarterly operations with minimal training overhead.

### 3.3 Reliability and Operational Control

1. Quarter lifecycle controls shall prevent unauthorized late modifications.
2. Critical import failures shall avoid partial inconsistent data.
3. Notifications and reminders shall support deadline adherence.

### 3.4 Security and Compliance Support

1. Access must be controlled by authenticated roles and organizational scope.
2. Sensitive operational evidence must be handled with restricted permissions.
3. The system should support departmental governance and reporting accountability obligations.

---

## 4. Open Decisions Required From Client

The following requirements are identified as pending client clarification:

1. **Hierarchy source of truth**
   - Use `PROGRAMME` / `SUB-PROGRAMME` spreadsheet columns when populated, or derive hierarchy from `Directorate_Name` codes.
2. **Directorate normalization policy**
   - Whether minor naming variations should be auto-normalized during import.
3. **Cross-year KPI duplicate policy**
   - Whether same KPI text across years should update existing records or create year-specific KPI records.
4. **Target value representation policy**
   - Confirm continued storage of mixed target formats (numbers, dates, text such as "30 days") as text fields where needed.

---

## 5. Out of Scope (Current Baseline)

Unless otherwise approved by the client, the following are out of current baseline scope:

1. Redesign of core hierarchy data model beyond Programme/Sub-Programme/Directorate/KPI chain.
2. Budget analytics tied to KPI import fields (budget was identified as not imported in current design).
3. Non-OPMS enterprise integrations not documented in current project materials.
4. Major workflow changes that bypass Director and GM approvals.

---

## 6. Acceptance-Oriented Deliverables

For delivery acceptance, the client is expecting:

1. A functioning OPMS module stack covering KPI management, workflow, evidence, dashboards, and portal usage.
2. Working Excel import for KPI onboarding with validation and history.
3. Enforced role-based permissions and organizational assignment logic.
4. Quarterly submission and approval lifecycle with traceable outputs.
5. Reporting capability suitable for management and legislature-facing performance reporting.
