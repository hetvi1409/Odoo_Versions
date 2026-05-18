# OPMS Module — Full Context Reference

> **Maintained Living Document** — Update this file whenever code, views, data, or behaviour changes.
> Version: 18.0.1.1.0 | Last updated: 2026-05-12

---

## 1. Module Overview

**Module name:** `opms_ecdhs`
**Full name:** ECDHS OPMS — Operational Performance Management System
**Odoo version:** 18.0
**Author:** ECDHS (Eastern Cape Department of Human Settlements)
**License:** LGPL-3
**Category:** Productivity
**Application:** Yes | Installable: Yes | Auto-install: No

### Purpose
OPMS is a performance planning and reporting system built on Odoo 18 for ECDHS. It manages the full cycle from APP (Annual Performance Plan) import through to quarterly submission, evidence upload, director review and approval, and performance reporting.

### Dependencies
`base`, `mail`, `account`, `portal`, `website`, `documents_spreadsheet`, `spreadsheet_dashboard`
External Python: `openpyxl`, `reportlab`

---

## 2. Data Hierarchy / Model Structure

The core hierarchy flows top-down:

```
APP Plan (opms.app.plan)
 └─ Programme (opms.programme)
     └─ Sub-Programme (opms.sub.programme)
         └─ Directorate (opms.directorate)
             └─ Output (opms.output)
                 └─ Output Indicator (opms.output.indicator)
                     └─ Annual (opms.annual)  [Indicator × Year × APP Plan]
                         └─ Annual Target (opms.annual.target)
                             └─ Quarterly Target (opms.quarterly.target)
                                 └─ Reporting Submission (opms.reporting.submission)
                                 └─ Narrative (opms.narrative)
                                 └─ Evidence (opms.evidence)
                         └─ Quarter (opms.quarter)  [Q1-Q4 per APP Plan × Year]
```

All operational models carry denormalised `programme_id`, `sub_programme_id`, `directorate_id`, `output_id`, `output_indicator_id`, `app_plan_id`, `financial_year`, `quarter_id` for fast filtering and reporting.

---

## 3. Models — Detailed Reference

### 3.1 `opms.app.plan`
- Top-level plan record. Linked to an `account.fiscal.year`.
- Has unique constraint on `(name, financial_year)`.
- `active` flag only toggles the APP Plan record itself; child records are not deactivated/deleted on plan deactivate.
- `unlink()` cascades deletion of versioned Excel import files from the module's `/data/` directory.
- Fiscal years are auto-created (April–March, SA government) by `_ensure_opms_fiscal_years()` — called in `post_init_hook` and by a scheduled cron.

### 3.2 `opms.programme`
- Top-level organisational unit.
- Unique on `(code, name)`.
- Fallback names for codes 1–4 defined in `PROGRAMME_FALLBACK` constant (used in import).
- Carries `One2many` counts for sub-programmes, directorates, outputs, indicators, targets, submissions.

### 3.3 `opms.sub.programme`
- Belongs to a Programme.
- Unique on `(programme_id, code, name)`.
- Fallback names for codes 1.1–4.3 defined in `SUB_PROGRAMME_FALLBACK` constant.

### 3.4 `opms.directorate`
- Belongs to a Sub-Programme.
- `programme_id` is a stored related field via `sub_programme_id.programme_id`.
- Unique on `(sub_programme_id, code, name)`.

### 3.5 `opms.output`
- Belongs to a Directorate.
- `sub_programme_id` and `programme_id` are stored related fields.
- Unique on `(directorate_id, code, name)`.

### 3.6 `opms.output.indicator`
Key fields:
| Field | Type | Notes |
|---|---|---|
| `name` | Char | Indicator description |
| `indicator_type` | Selection | `app` (APP) / `aop` (AOP) |
| `measurement_type` | Selection | number / percentage / date / boolean / milestone / text |
| `measurement_unit` | Char | Optional unit (e.g. "houses"), only for `number` type |
| `aggregation_rule` | Selection | sum / count / latest / max / min / average / any / all |
| `comparison_direction` | Selection | higher / lower / exact |
| `output_id` | Many2one | Required, `ondelete=restrict` |

**Auto-defaults when `measurement_type` changes** (via `create`, `write`, `_onchange_measurement_type`):
| Type | Aggregation | Comparison |
|---|---|---|
| number | sum | higher |
| percentage | average | higher |
| date | latest | lower |
| boolean | latest | exact |
| milestone | latest | exact |
| text | latest | exact |

**Import behaviour:** When imported via Excel, `measurement_type` defaults to `number` if no column is present, and aggregation/comparison are auto-derived from the type. Optional columns `Measurement_Type`, `Aggregation_Rule`, `Comparison_Direction`, `Measurement_Unit` can override defaults.

Unique on `(output_id, name, indicator_type)`.

**Key methods:**
- `_aggregate_submission_actuals(submissions, preview_actual)` — aggregates actual values per rule
- `_compare_target_and_actual(planned_value, actual_value)` — returns status (`unknown`/`behind`/`met`/`exceeded`), deviation display, and note
- `_format_value_for_indicator(value)` — format for display per measurement type
- `_parse_target_value(value)` — parse raw string to typed value

### 3.7 `opms.annual`
- Bridge record: one per `(output_indicator_id, app_plan_id, financial_year)`.
- Auto-created/linked by `opms.annual.target._sync_annual_id()`.
- `name` is computed as `"{indicator_name} - {fiscal_year}"`.

### 3.8 `opms.annual.target`
- One per `(output_indicator_id, financial_year)` — unique constraint.
- `target_value` is a `Char` validated against `measurement_type` on save.
- Backend form now shows inline target-format guidance (`target_value_guidance`) with examples per measurement type (number, percentage, date, boolean, milestone, text).
- **Target text storage:** OPMS stores annual target values as text and parses them according to the linked indicator measurement type at validation, formatting, aggregation, and comparison time.
- Accepted text examples: number (`30`), percentage (`95` or `95%`), date (`2026-03-31` or `31/03/2026`), boolean (`yes`/`no`), milestone/text (free text).
- Computes `actual_value_display`, `variance_display`, `achievement_status`, `comparison_note` from aggregated submissions.
- `_generate_quarterly_targets(overwrite=False)` — splits annual value into Q1–Q4 targets (integer division, remainder distributed Q1-first). For non-numeric values, same value is copied to all quarters.
- On `create`, auto-generates quarterly targets unless `context.get('import_file')` is set.
- `_get_or_create_annual()` — finds or creates the parent `opms.annual` record.

### 3.9 `opms.quarter`
- Represents Q1–Q4 for a given `(app_plan_id, financial_year)`.
- Unique on `(app_plan_id, financial_year, code)`.
- **Submission window management:**
  - `submission_open_date`, `submission_close_date` — auto-defaulted if not set (first of the quarter month, 9-day window).
  - `submission_period_state` — `open`/`closed`, auto-synced by cron and on every `write()`.
  - `submission_manual_override` — disables auto-sync; auto-expires on `manual_override_until`.
  - `_apply_manual_submission_state(action_type)` — force open/close with override expiry calculation.
  - `_raise_if_submission_closed()` — guards submission creation/transitions.
    - **Form and list-view controls:** the module supports open/close control from the single-quarter flow and from list-view multi actions via `action_force_open_selected_quarters` and `action_force_close_selected_quarters`.
- **Reminder emails:** 6 scheduled reminder types (15th/25th of prior month, day-before-open, open day, day-before-close, close day). Sent by `_process_submission_reminders()`.
- `_cron_process_submission_periods()` — daily cron: syncs period state and processes reminders.
- Reminder sent-on tracking fields prevent duplicate sends per cycle.

### 3.10 `opms.quarterly.target`
- Belongs to `annual_target_id` and `quarter_id`.
- `planned_target` Char validated against measurement type.
- Backend form now shows inline planned-target format guidance (`planned_target_guidance`) with examples per measurement type.
- **Target text storage:** quarterly planned targets are also stored as text so the same field supports numeric, date, boolean, milestone, percentage, and free-text indicators.
- Computes actual progress via `_compute_actual_progress` (same aggregation/comparison logic as annual target).
- Unique on `(annual_target_id, quarter_id)`.
- All hierarchy fields stored as related fields for fast querying.

### 3.11 `opms.narrative`
- Linked to a `quarterly_target_id` (required). Also indexed on all hierarchy fields.
- `reporting_submission_id` — optional link to submission (set when submitted via portal).
- Can have child evidence records.

### 3.12 `opms.evidence`
- Linked to `quarterly_target_id` (required, cascade on delete).
- `file` (Binary) + `file_name` (Char) — PDF only (portal enforces `.pdf` extension).
- `storage_path` — computed filesystem path under `opms_ecdhs.evidence_root` config param (or `<data_dir>/opms_evidence`). Directory: `evidence/{year}/{quarter}/{directorate_slug}/`.
- On create/write/unlink, triggers `_sync_workflow_status_with_evidence()` on linked submissions.
- Download/view actions at `/my/opms/evidence/{id}/file`.

### 3.13 `opms.reporting.submission`
- Core submission record.
- **Key fields:** `name`, `quarterly_target_id`, `submitted_by`, `submission_date`, `workflow_status`, `actual_value`, `comments` (Progress), `reason_for_deviation`, `remedial_actions`, `rejection_reason`.
- **Workflow statuses:** `draft` → `submitted` → `director_review` → `approved` / `rejected`.
- `actual_value` is normalised on save (numbers stripped of units, dates normalised to YYYY-MM-DD, booleans to "Yes"/"No").
- `actual_value_guidance` (Html) — computed inline guidance for submission form based on measurement type.
- Submission creation/transition to `submitted` enforces quarter open check (bypassed with `context['opms_allow_closed_submission_seed']`).
- **Notifications:**
    - On status → `submitted`: `_notify_managers_submission_completed()` — notifies OPMS Managers linked to the submission's directorate.
    - On status → `rejected`: `_notify_submitter_submission_rejected()` — notifies the submitter.
    - **Non-blocking delivery:** OPMS notification emails are queued (`mail.mail`) and sent by the mail queue cron (no synchronous `.send()` in request flow) so portal/manual actions are not delayed by SMTP.
- **Rejected reset flow:** Rejected submissions now include `action_reset_to_draft()` to move status back to `draft` and clear `rejection_reason`.
- `_sync_workflow_status_with_evidence()` — called whenever evidence changes; may auto-advance status when evidence is uploaded.
- All hierarchy fields stored as related/denormalised fields.

---

## 4. Supporting Models

### 4.1 `opms.user.management`
- One profile per user (unique on `user_id`).
- Duplicate-profile protection is enforced both by SQL unique constraint and explicit model validation, including inactive profiles.
- Scopes: `company_id` (Region/Office), `programme_ids`, `sub_programme_ids`, `directorate_ids`.
- Mandatory on create/update: `user_id`, `company_id`, at least one `programme_id`, at least one `sub_programme_id`, and at least one `directorate_id`.
- Company sync behavior with `res.users.company_id`:
    - If selected user already has `company_id`, OPMS profile `company_id` is forced to that same value.
    - If selected user has no `company_id`, OPMS profile selection for Region/Office also writes back to `res.users.company_id`.
- Role flags: `is_opms_submissions_user`, `is_opms_manager`, `is_opms_director`.
- On create/write/unlink: `_sync_user_groups()` — updates `res.groups` membership, then `_sync_opms_scope_from_profile()` on `res.users`, then re-applies access policy.
- Hierarchy integrity constraint: sub-programmes must belong to selected programmes; directorates must belong to selected sub-programmes.
- This is the core OPMS User Management feature: it controls both user role assignment and the scope data later enforced by OPMS access controls.

### 4.2 `opms.access.policy.service` (AbstractModel)
- Manages record rules via `ir.rule` domain expressions per scoped group.
- Config params: `opms_ecdhs.access.level` (off/basic/strict), `opms_ecdhs.access.limit_company`, `opms_ecdhs.access.limit_programme`, `opms_ecdhs.access.limit_sub_programme`, `opms_ecdhs.access.limit_directorate`, `opms_ecdhs.access.empty_behavior` (allow/deny), `opms_ecdhs.access.require_active_profile`, `opms_ecdhs.access.applies_to` (profiled/opms_groups/both), `opms_ecdhs.access.admin_bypass`.
- `apply_policy()` — reads config, rebuilds record rule domains, assigns/removes users from `group_opms_scoped_access`.
- Rule targets: `basic` level applies to operational data (annual targets through submissions); `strict` also applies to hierarchy models (programme through output indicator) and app plans/quarters.
- In Settings this appears under **OPMS User Data Access Controls**, including the reset-to-relaxed-defaults action.
- Configuration menus also include **Email Templates** (OPMS `mail.template` records only) and a standalone **OPMS Emails** menu that opens `mail.mail` filtered to OPMS-generated outgoing emails.

### 4.3 `opms.label.service` (AbstractModel)
- Dynamic terminology system — all menu labels, field labels, and heading text are configurable.
- Configurable terms: `app_plan`, `programme`, `sub_programme`, `directorate`, `outcome`, `output`, `output_indicator`, `annual`, `quarterly_target`, `quarter`.
- Each term has `singular`, `plural` variants.
- Options stored in `ir.config_parameter`. Custom overrides stored as JSON in `opms_ecdhs.labels.custom_overrides`.
- `get_effective_terms()` — returns active label map. `apply_backend_labels()` — updates menu item names. `apply_frontend_labels()` — updates portal page headings.
- Frontend: `opms_dynamic_labels_frontend.js` fetches labels via `/opms/labels/frontend` and applies to DOM. Backend: `opms_dynamic_labels_backend.js` updates menu items via `/opms/labels/backend`.
- In Settings this appears under **OPMS Dynamic Terminology**.

### 4.4 `opms.live.report.sync`
- Links a spreadsheet document (`documents.document`) and/or dashboard (`spreadsheet.dashboard`) to a JSON report payload.
- `refresh_from_backend()` — regenerates spreadsheet snapshot from the correct report engine (`app_annual` or `sub_entity`) and writes to the linked document/dashboard.
- `refresh_links_for_scope()` — refreshes only impacted live links when relevant OPMS backend records change.
- `cron_refresh_live_links()` — scheduled safety refresh for all active auto-refresh links.
- `register_or_update_link()` — upserts a sync record.
- `DocumentsDocument.write()` is extended to propagate spreadsheet changes to linked dashboards (unless `context['opms_skip_live_sync_propagation']`).
- `SpreadsheetRevision.create()` is extended so manual spreadsheet edits saved as collaborative revisions are immediately mirrored to linked dashboards.
- Live backend-trigger refresh is attached to changes on: `opms.programme`, `opms.sub.programme`, `opms.directorate`, `opms.output`, `opms.output.indicator`, `opms.annual.target`, and `opms.quarterly.target`.
- **Live Sync Trigger Architecture**: Each of the 7 inheriting model classes (`OpmsProgrammeLiveSync`, `OpmsSubProgrammeLiveSync`, `OpmsDirectorateLiveSync`, `OpmsOutputLiveSync`, `OpmsOutputIndicatorLiveSync`, `OpmsAnnualTargetLiveSync`, `OpmsQuarterlyTargetLiveSync`) defines its own `create`, `write`, and `unlink` overrides using `super()` (no-argument form). Shared helper logic (`_opms_live_sync_scope_snapshot`, `_opms_trigger_live_sync_refresh`) lives as module-level functions assigned to each class. **Do not** use the `super(type(self), self)` pattern or class-attribute method assignment (`create = SomeClass.create`) — this causes infinite recursion because Python's MRO cannot resolve `super()` correctly when the method is copied rather than inherited.
- **Import Recursion Prevention**: During bulk imports, the context flags `opms_skip_live_sync_refresh=True` and `opms_import_app_matrix=True` are set to prevent live sync triggers from firing on each record creation. After import completes successfully, a single `refresh_links_for_scope()` call updates all affected links. This prevents redundant refreshes during bulk operations.
- Effective behavior:
    - If OPMS backend report data changes, impacted live spreadsheets are rebuilt immediately from backend data.
    - If a linked spreadsheet is edited/updated, the linked dashboard is pushed with the latest spreadsheet payload.
    - If edits are stored as collaborative revisions (manual spreadsheet edits), linked dashboards are updated in the same save path.
    - If bulk imported, all record creation is batched without refresh, then a single sweep refreshes all impacted links post-import.

### 4.5 `opms.import.history` / `opms.import.history.line`
- Tracks every import operation and each row processed.
- Versioned Excel filename stored for corrected-file re-imports.
- Accessible at Admin → Import History / Import History Lines.

### 4.6 `res.users` (inherited)
- Added fields: `opms_is_submissions_user`, `opms_is_manager` (computed from `groups_id`); `opms_scope_profile_active`, `opms_scope_company_id`, `opms_scope_programme_ids`, `opms_scope_sub_programme_ids`, `opms_scope_directorate_ids` (synced from `opms.user.management`).
- Reliability hardening: OPMS scope fields now use explicit relation table names (`res_users_opms_programme_rel`, `res_users_opms_sub_programme_rel`, `res_users_opms_directorate_rel`) and indexed profile/company columns to keep schema stable across environments and improve scoped-access lookups.

### 4.7 Target Values As Text
- Both annual and quarterly targets use text fields in the database.
- OPMS intentionally converts these values to typed runtime values only when needed.
- This is why one target field design can support number, percentage, date, boolean, milestone, and text indicators.

---

## 5. Wizards

| Wizard Model | Purpose |
|---|---|
| `opms.app.import.wizard` | Import APP matrix from Excel, copy from previous year, or load demo submissions |
| `opms.submission.period.wizard` | Force-open or force-close a quarter's submission window |
| `opms.submission.reminder.wizard` | Send ad-hoc submission window reminder emails |
| `opms.submission.notification.wizard` | Send manager/submitter notification for selected submissions |
| `opms.rejection.reason.wizard` | Capture rejection reason and set submission to rejected |
| `opms.app.annual.report.wizard` | Select programme and print APP Annual Report (PDF) |
| `opms.sub.entity.report.wizard` | Shared OPMS Reports wizard for APP Annual and Sub-Programme / Directorate reports; supports PDF, spreadsheet, dashboard sync, and generated links |

### OPMS Reports Wizard (`opms.sub.entity.report.wizard`)
- Shared wizard used for both `app_annual` and `sub_entity` report templates.
- APP Annual Report now supports the same output pipeline as the sub-entity report:
    - PDF output
    - Spreadsheet generation
    - Dashboard create/update flow
    - Generated links flow
- `spreadsheet_sync_mode` is only shown and required when `output_mode = spreadsheet`.
- `dashboard_sync_mode` (Dashboard Options section) and the **Generate and Show Links** button are only visible when `output_mode = spreadsheet`.
- If `report_scope = both`, changing the selected sub-programme clears any directorate that no longer belongs to it.

### Import Wizard (`opms.app.import.wizard`) Details
**Operation modes:**
- `manual_import` — upload an `.xlsx` file
- `auto_import` — use bundled module Excel or a previously corrected version
- `copy_previous` — duplicate hierarchy from a source financial year
- `demo_app_plans` — generate a full demo APP Plan hierarchy (APP Plan → Programme → Sub-Programme → Directorate → Output → Output Indicator → Annual Target → Quarters → Quarterly Targets) with randomised planned values; indicator source is configurable (URL, local PDF, uploaded PDF, bundled Excel, or built-in fallback set). Admin-only.
- `demo_submissions` — seed demo reporting submissions with random workflow states and evidence (was Option 3, now **Option 4**). Admin-only.

**Required Excel columns (with aliases):** `Directorate_Name`, `Output_ Indicator`, `Indicator_Type`, `Annual_Target`, `Q1_Planned`, `Q2_Planned`, `Q3_Planned`, `Q4_Planned`

**Optional columns:** `Programme_Code`, `Sub_Programme_Code`, `Output_Name`, `Measurement_Type`, `Aggregation_Rule`, `Comparison_Direction`, `Measurement_Unit`

**Import behaviour:**
- Looks up/creates Programme → Sub-Programme → Directorate → Output → Output Indicator chain.
- Indicator `measurement_type` defaults to `number` if column absent; aggregation/comparison auto-derived.
- `import_mode`: `create` (create new, skip existing), `update` (update existing), `skip` (no-op if exists).
- Quarterly targets created from Q1–Q4 columns directly (not via auto-split).
- **Performance & Recursion Prevention**: The full APP import action runs under both `context['opms_skip_live_sync_refresh']=True` and `context['opms_import_app_matrix']=True`, and all upsert operations (search/create/write) for hierarchy/target models keep those contexts. Live-sync trigger hooks explicitly skip when either flag is present, preventing recursive live sync calls for both create and update paths. After all rows imported successfully, a single `refresh_links_for_scope()` call updates all affected live sync links.
- **Manual / Auto Import Performance**: repeated hierarchy lookups are cached in-memory within a single import run (APP Plan, Programme, Sub-Programme, Directorate, Output, Indicator, Annual Target, Quarter, Quarterly Target) and import history lines are inserted in batches instead of one row at a time.
- **Manual / Auto Import Progress Feedback**: the import now emits staged in-session progress notifications at startup, every configured number of processed rows, and on completion so large Excel files no longer appear silent while running.
- **Copy Previous Period Performance**: `copy_previous` now preloads target plans, target quarters, target annual targets, and existing target quarterly targets, and groups source quarterly targets by annual target to avoid repeated inner-loop `search(..., limit=1)` calls.
- **Import / Copy Progress Tuning**: runtime tuning is available via `ir.config_parameter` keys `opms_ecdhs.app_import_notify_step`, `opms_ecdhs.app_import_history_batch_size`, and `opms_ecdhs.copy_previous_notify_step`.
- **Failure diagnostics**: Import row failures now log full Python traceback to server logs and include a traceback snippet in `opms.import.history.line.message` for faster root-cause analysis.

---

## 6. Controllers (`controllers/`)

### 6.1 `portal_submission.py` — `OpmsPortalSubmission`
Portal web controller. Key routes:

| Route | Method | Purpose |
|---|---|---|
| `/my/opms` | GET | Portal home — list open quarterly targets for the user |
| `/my/opms/<int:target_id>` | GET/POST | Submission form for a quarterly target |
| `/my/opms/submission/<int:submission_id>` | GET | View submitted submission |
| `/my/opms/evidence/<int:evidence_id>/file` | GET | Download/view evidence file |
| `/my/opms/user-management` | GET/POST | Admin-only OPMS User Management UI |
| `/opms/labels/frontend` | GET/POST | Serve/receive frontend label configuration |
| `/opms/labels/backend` | GET | Serve backend label JSON |
| `/opms/import/template/download` | GET | Download Excel import template |

**Security constraints:**
- Max 10 files per submission, 10 MB per file, 25 MB total upload.
- Only `.pdf` files accepted.
- Max 2000 chars for text fields, 100 chars for `actual_value`.
- User management admin requires `base.group_system` or `base.group_erp_manager`.

**Frontend filter UX (portal templates):**
- `/my/opms/view` Hierarchy Filters are displayed in two ordered columns:
    - Left: Financial Year → Programme → Sub-Programme → Directorate
    - Right: Output → Output Indicator → Quarter → Status
- Frontend filtering selects are enhanced with typed search + dropdown behavior (keep dropdown selection, type to narrow options, show `- No Match -` when no option matches typed input).
- Search enhancement is provided by `static/src/js/opms_searchable_selects_frontend.js` and styling in `static/src/css/opms_portal.css`.

### 6.2 `import_template.py`
Generates and serves the Excel import template file for download.

### 6.3 `opms_labels.py`
JSON endpoints for dynamic labels (frontend/backend).

---

## 7. Reports

### 7.1 APP Annual Report
- Model: `report.opms_ecdhs.report_opms_app_annual_template`
- Action: `opms_ecdhs.action_report_opms_app_annual_report`
- Template: `reports/opms_app_annual_report_template.xml`
- Direct PDF wizard: `opms.app.annual.report.wizard`
- Shared reporting wizard support: `opms.sub.entity.report.wizard` can also generate APP Annual output as PDF, spreadsheet, and dashboard-linked content.
- Shows indicators across 5 audited years + 1 estimated year + 3 MTDP years (South African MTDP planning horizon).

### 7.2 Sub-Entity Report (Sub-Programme / Directorate)
- Model: `report.opms_ecdhs.report_opms_sub_entity_template`
- Action: `opms_ecdhs.action_report_opms_sub_entity_report`
- Template: `reports/opms_sub_entity_report_template.xml`
- Wizard: `opms.sub.entity.report.wizard`
- Output: PDF or Spreadsheet
- Spreadsheet sync: can create/update a `documents.document` spreadsheet and/or a `spreadsheet.dashboard`.
- Scope: Sub-Programme, Directorate, or Both.
- Shows Q1–Q4 planned targets, actual values, status per indicator.

---

## 8. Security

### Groups
| Group XML ID | Name | Purpose |
|---|---|---|
| `group_opms_submissions_user` | OPMS Submissions Users | Receive reminders; can submit via portal |
| `group_opms_manager` | OPMS Managers | Manage operations; receive submission alerts |
| `group_opms_director` | OPMS Directors | Oversight; receive reminders |
| `group_opms_scoped_access` | OPMS Scoped Data Access | Governed by configurable record rules |

### Model-Level Access (ir.model.access.csv)
- All OPMS models: full CRUD for `base.group_user` (internal users).
- Portal users: read-only on hierarchy/target models; full CRUD on submissions, narratives, evidence.
- `opms.live.report.sync` and `opms.user.management`: restricted to `base.group_system` and `base.group_erp_manager`.

### Record Rules (`security/opms_access_rules.xml`)
- Scoped rules applied dynamically via `opms.access.policy.service` based on OPMS Settings.
- Rules target programme, sub-programme, directorate, output, output indicator, app plan, quarter, and all operational data models.
- Rule domain expressions are Python code strings referencing `user.opms_scope_*` fields.

---

## 9. Menu Structure

```
OPMS (root)
├── Submission Portal          → /my/opms
├── Programmes
│   ├── APP Plans
│   ├── Programmes
│   ├── Sub-Programmes
│   └── Directorates
├── Outputs
│   ├── Outputs
│   └── Output Indicators
├── Annuals
│   ├── Indicator Years
│   └── Annual Targets
├── Quarters
│   ├── Quarters
│   └── Quarterly Targets
├── Reporting
│   ├── Narratives
│   ├── Evidence
│   ├── Reporting Submissions
│   └── Reports Generator
├── Administration
    ├── Download Import Template
    ├── Import APP Matrix
    │   ├── Operation: Manual File Import
    │   │   ├── Validate File (no write)
    │   │   └── Import APP Matrix (write using selected import mode)
    │   ├── Operation: Auto-Import (Bundled or Corrected Excel)
    │   │   └── Auto-Import Bundled Excel
    │   ├── Operation: Copy from Previous Period
    │   │   └── Copy APP hierarchy + targets to selected target year
    │   └── Operation: Load Demo Submissions (Settings/Admin only)
    │       └── Seed demo submissions for selected financial year
    ├── Import History
    └── Import History Lines
└── Configurations
    ├── Settings
    ├── User Management
    ├── Email Templates
    └── OPMS Emails
```

Functional breakdown notes:
- Reporting -> Reports Generator opens the shared OPMS Reports wizard for APP Annual and Sub-Entity reporting, with PDF or Spreadsheet output, optional spreadsheet sync, optional dashboard create/update, and generated links.
- Quarters -> Quarters list includes mass actions (from list-view Actions): Open Selected Quarters Now and Close Selected Quarters Now.
- Configurations -> User Management opens the portal/admin management UI at `/my/opms/user-management` (URL action), while Settings opens the standalone OPMS settings form.

All menu labels are dynamic via `opms.label.service`.

---

## 10. Data / Cron Jobs

| Cron | Model | Method | Schedule | Purpose |
|---|---|---|---|---|
| Fiscal Year Generator | `opms.app.plan` | `_ensure_opms_fiscal_years` | Yearly (via data XML) | Creates April–March fiscal years |
| Submission Period Sync | `opms.quarter` | `_cron_process_submission_periods` | Daily | Syncs open/close state; sends scheduled reminders |
| Live Sync Refresh | `opms.live.report.sync` | `cron_refresh_live_links` | Daily | Refreshes spreadsheet/dashboard report snapshots |

---

## 11. Static Assets

### CSS
- `opms_backend.css` — backend form/list styling
- `opms_portal.css` — portal submission form styling

### JavaScript
- `opms_dynamic_labels_backend.js` — fetches `/opms/labels/backend` and renames menu items in the backend
- `opms_dynamic_labels_frontend.js` — fetches `/opms/labels/frontend` and applies terminology overrides in the portal

### Samples
- Sample Excel import template in `static/src/samples/`

---

## 12. Post-Install Hook (`hooks.py`)

```python
def post_init_hook(env):
    env["opms.app.plan"]._ensure_opms_fiscal_years()     # Create SA fiscal years 2020–current
    env["opms.annual.target"]._backfill_annual_links()   # Link annual targets to opms.annual records
    env["opms.label.service"].apply_backend_labels()     # Apply stored terminology to menus
    env["opms.access.policy.service"].sudo().apply_policy()  # Apply access record rules
```

---

## 13. Settings (res.config.settings)

All settings are stored as `ir.config_parameter` keys:

| Setting | Param Key | Purpose |
|---|---|---|
| Enable Narratives | `opms_ecdhs.enable_narratives` | Show/hide narrative field on portal |
| Data Access Level | `opms_ecdhs.access.level` | off / basic / strict |
| Apply Limits To | `opms_ecdhs.access.applies_to` | profiled / opms_groups / both |
| Require Active Profile | `opms_ecdhs.access.require_active_profile` | Bool |
| Admin Bypass | `opms_ecdhs.access.admin_bypass` | Bool |
| Limit Company | `opms_ecdhs.access.limit_company` | Bool |
| Limit Programme | `opms_ecdhs.access.limit_programme` | Bool |
| Limit Sub-Programme | `opms_ecdhs.access.limit_sub_programme` | Bool |
| Limit Directorate | `opms_ecdhs.access.limit_directorate` | Bool |
| Empty Behavior | `opms_ecdhs.access.empty_behavior` | allow / deny |
| APP Import Progress Notify Step | `opms_ecdhs.app_import_notify_step` | Rows between APP import progress checkpoints |
| APP Import History Batch Size | `opms_ecdhs.app_import_history_batch_size` | Batch size for `opms.import.history.line` inserts |
| Copy Previous Progress Notify Step | `opms_ecdhs.copy_previous_notify_step` | APP Plans between copy-previous progress checkpoints |
| Demo Seed Chunk Size | `opms_ecdhs.demo_seed_chunk_size` | Demo submission create batch size |
| Demo Seed Preparation Notify Step | `opms_ecdhs.demo_seed_prep_notify_step` | Targets between demo-seed prep checkpoints |
| Demo Seed Create Notify Every Chunks | `opms_ecdhs.demo_seed_create_notify_every_chunks` | Demo-seed create batches between progress checkpoints |
| Dynamic labels (per term) | `opms_ecdhs.labels.<term>.<singular\|plural>` | Per-term label overrides |
| Custom label overrides JSON | `opms_ecdhs.labels.custom_overrides` | Full JSON blob |
| Evidence root path | `opms_ecdhs.evidence_root` | Filesystem path for evidence storage |

### Settings Blocks
- **Submission Features** — contains the Enable/Disable Narratives setting.
- **Import Performance** — contains admin tuning for APP import progress frequency, import history batching, copy-previous progress frequency, and demo seed chunk/progress behavior.
- **OPMS User Data Access Controls** — contains access level, applies-to mode, profile requirement, admin bypass, scope limits, empty behavior, and reset action.
- **OPMS Dynamic Terminology** — contains label/terminology overrides and reset functionality.

### Enable / Disable Narratives
- Controlled by `opms_ecdhs.enable_narratives`.
- When enabled, the portal submission form shows the narrative input and related narrative-facing behaviour remains visible.
- When disabled, the optional narrative input is hidden from the submission UX without removing the model itself.

---

## 14. Email Notifications

| Trigger | Recipients | Template/Method |
|---|---|---|
| Submission window 15th of prior month | Submissions Users + Managers + Directors | `_process_submission_reminders` |
| Submission window 25th of prior month | Submissions Users + Managers + Directors | `_process_submission_reminders` |
| 1 day before open | Submissions Users + Managers + Directors | `_process_submission_reminders` |
| Opening day | Submissions Users + Managers + Directors | `_process_submission_reminders` |
| 1 day before close | Submissions Users + Managers + Directors | `_process_submission_reminders` |
| Closing day | Submissions Users + Managers + Directors | `_process_submission_reminders` |
| Manual/custom reminder (wizard) | Same | `OpmsSubmissionReminderWizard` |
| Submission submitted | OPMS Managers (linked to directorate) | `_notify_managers_submission_completed` |
| Submission rejected | Submitter | `_notify_submitter_submission_rejected` |

Mail template: `opms_ecdhs.mail_template_opms_submission_reminder`
All emails also posted to chatter on the quarter record.

### Quarter Submission Reminder Types
- `pre_open_15` — 15th of prior month reminder
- `pre_open_25` — 25th of prior month reminder
- `before_open` — one day before opening reminder
- `open_day` — opening day reminder
- `before_close` — one day before closing reminder
- `close_day` — closing day reminder
- `custom` — manual reminder sent from the reminder wizard

### Submission Notifications
- Manager notification is triggered when a submission reaches `submitted` and targets active OPMS managers linked to the submission's directorate.
- Rejection notification is triggered when a submission reaches `rejected` and sends the rejection reason back to the submitter.
- Manual resend/support flows exist through `opms.submission.notification.wizard`.

---

## 15. Measurement Type Reference

| Type | Aggregation Default | Comparison Default | Parse/Validate | Display Format |
|---|---|---|---|---|
| number | sum | higher | numeric (float) | integer if whole, else 2dp |
| percentage | average | higher | numeric (float) | same + `%` suffix |
| date | latest | lower | YYYY-MM-DD / DD/MM/YYYY | DD/MM/YYYY |
| boolean | latest | exact | yes/no/true/false/1/0 | Yes / No |
| milestone | latest | exact | free text | text |
| text | latest | exact | free text | text |

**Achievement Status logic (`_compare_target_and_actual`):**
- Number/Percentage + `higher`: actual > planned → exceeded; actual < planned → behind; equal → met
- Number/Percentage + `lower`: actual < planned → exceeded; actual > planned → behind
- Number/Percentage + `exact`: actual == planned → met; else → behind
- Date: days early → exceeded; days late → behind; on target → met
- Boolean: matches → met; else → behind
- Text/Milestone: exact text match → met; else → behind (milestone) or unknown (text)

---

## 16. Portal Submission Workflow

1. Portal/internal user navigates to `/my/opms`.
2. Sees list of open quarterly targets (filtered by open quarter window and user's directorate scope).
3. Opens a target → fills in: `actual_value`, `comments` (Progress), optionally `reason_for_deviation`, `remedial_actions`, `narrative_text`, uploads PDF evidence files.
4. Submits → status moves `draft` → `submitted`; managers notified.
5. Manager reviews → moves to `director_review` or `approved` or opens rejection wizard.
6. If rejected → submitter notified with rejection reason.

---

## 17. Key Constants

```python
PROGRAMME_FALLBACK = { "1": "Administration", "2": "Integrated Human Settlements Development", "3": "Housing Development", "4": "Housing Asset Management" }
SUB_PROGRAMME_FALLBACK = { "1.1": "Executive Leadership", ..., "4.3": "Social and Rental Housing" }
MEASUREMENT_TYPE_SELECTION = [number, percentage, date, boolean, milestone, text]
AGGREGATION_RULE_SELECTION = [sum, count, latest, max, min, average, any, all]
TARGET_STATUS_SELECTION = [unknown, behind, met, exceeded]
COMPARISON_DIRECTION_SELECTION = [higher, lower, exact]
```

---

## 18. File Structure

```
opms_ecdhs/
├── __init__.py
├── __manifest__.py
├── hooks.py                        # post_init_hook
├── OPMS.md                         # This file
├── controllers/
│   ├── portal_submission.py        # Main portal + user management controller
│   ├── import_template.py          # Excel template download
│   └── opms_labels.py              # Dynamic labels JSON endpoints
├── data/
│   ├── opms_fiscal_year_cron.xml
│   ├── opms_live_sync_cron.xml
│   ├── opms_spreadsheet_dashboard_group.xml
│   └── opms_submission_reminder_templates.xml
├── demo/
│   └── portal_user_demo.xml
├── models/
│   ├── opms_models.py              # All core models (AppPlan → Submission)
│   ├── opms_labeling.py            # Dynamic label service
│   ├── opms_user_management.py     # User profile + group sync
│   ├── opms_access_policy.py       # Scoped access policy service
│   └── opms_live_report_sync.py    # Live spreadsheet/dashboard sync
├── reports/
│   ├── opms_app_annual_report.py   # APP Annual Report logic
│   ├── opms_app_annual_report_template.xml
│   ├── opms_app_annual_report_action.xml
│   ├── opms_sub_entity_report.py   # Sub-Entity Report logic
│   ├── opms_sub_entity_report_template.xml
│   └── opms_sub_entity_report_action.xml
├── security/
│   ├── opms_groups.xml
│   ├── opms_access_rules.xml
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── css/opms_backend.css
│       ├── css/opms_portal.css
│       ├── js/opms_dynamic_labels_backend.js
│       ├── js/opms_dynamic_labels_frontend.js
│       └── samples/                # Sample Excel import template
├── views/
│   ├── opms_views.xml              # Main views for all models
│   ├── opms_menus.xml
│   ├── opms_settings_views.xml
│   ├── opms_server_actions.xml
│   ├── opms_import_wizard_views.xml
│   ├── opms_submission_period_wizard_views.xml
│   ├── opms_submission_reminder_wizard_views.xml
│   ├── opms_submission_notification_wizard_views.xml
│   ├── opms_rejection_reason_wizard_views.xml
│   ├── opms_user_groups_views.xml
│   ├── opms_app_annual_report_wizard_views.xml
│   ├── opms_sub_entity_report_wizard_views.xml
│   └── portal_templates/
│       ├── opms_portal_submission_templates.xml
│       └── opms_portal_all_submissions.xml
└── wizard/
    ├── opms_app_import_wizard.py
    ├── opms_app_annual_report_wizard.py
    ├── opms_sub_entity_report_wizard.py
    ├── opms_submission_period_wizard.py
    ├── opms_submission_reminder_wizard.py
    ├── opms_submission_notification_wizard.py
    └── opms_rejection_reason_wizard.py
```

---

## 19. Change Log

| Date | Change Summary |
|---|---|
| 2026-05-12 | Initial full context document created |
| 2026-05-12 | Added explicit documentation for target text storage, dynamic terminology, user access controls, narratives setting, quarter open/close UI behaviour, reminder types, and manager/rejection notifications |
| 2026-05-12 | Updated report wizard context for APP Annual spreadsheet/dashboard support, spreadsheet-sync visibility rules, sub-programme/directorate dependency, and Reporting/Configurations menu moves |
| 2026-05-12 | Updated live sync context so backend OPMS report-data changes immediately refresh impacted spreadsheets and linked dashboards continue syncing from spreadsheet updates |
| 2026-05-12 | Added revision-level sync context: manual spreadsheet edits saved as collaborative revisions now mirror to linked dashboards immediately |
| 2026-05-13 | Fixed "maximum recursion depth exceeded" import failure by disabling live sync refresh triggers during APP Matrix bulk import and performing single refresh after all records imported |
| 2026-05-13 | Hardened OPMS user-scope schema by setting explicit Many2many relation table names and indexed scope fields on `res.users` extensions |
| 2026-05-13 | Strengthened APP import recursion guard by enforcing `opms_skip_live_sync_refresh` across full import execution and all upsert create/write paths |
| 2026-05-13 | Added second import guard flag (`opms_import_app_matrix`) in live-sync hooks and enabled row-level traceback logging for APP import failures |
| 2026-05-13 | **Root-cause fix**: replaced broken `OpmsLiveSyncTriggerBehavior` mixin class-assignment pattern (`create = OpmsLiveSyncTriggerBehavior.create`) with proper `super()` overrides in each of the 7 live-sync model classes. The old pattern caused `super(type(self), self)` to loop infinitely because Python MRO cannot resolve `super()` for an assigned (not inherited) method. Import APP Matrix now succeeds for all rows. |
| 2026-05-13 | Reporting submission UX and notifications updated: added **Reset to Draft** action for rejected submissions, hid dashboard-only report wizard controls when output format is not spreadsheet, and fixed Manager Submission Alert delivery for both manual sends and portal-driven submissions (email + chatter). |
| 2026-05-13 | Optimized OPMS notification performance by queuing manager/rejection emails for cron delivery (removed synchronous mail send from request path) and posting chatter with non-forced dispatch to prevent portal/manual submission delays. |
| 2026-05-13 | Added backend inline target-format helpers for Annual/Quarterly target entry (`target_value_guidance`, `planned_target_guidance`) with concrete examples for date and non-numeric measurement types. |
| 2026-05-13 | Updated display wording across backend and portal UI: status label **Behind/Behind Target** now shows as **Not-Achieved**, and **Variance** now shows as **Deviation**. Internal keys (`behind`, `variance_display`) were intentionally kept unchanged for safety. |
| 2026-05-13 | Updated portal filter UX: reordered `/my/opms/view` Hierarchy Filters into requested left/right sequence and added searchable dropdown filtering (with `- No Match -` feedback) across frontend filter fields. |
| 2026-05-13 | Fixed APP Plan deactivate behavior: toggling `active=False` no longer cascades `active=False` to all linked operational records. Child data now remains intact; only explicit unlink/delete performs cascade removal via `ondelete="cascade"`. |
| 2026-05-14 | Expanded Section 9 (Menu Structure) with deeper functional mapping, including Import APP Matrix operation modes/actions, Reports Generator capabilities, quarter bulk actions, and Configurations -> OPMS Emails. |
| 2026-05-14 | Optimized demo seed loading (`Option 3 — Load Demo Submissions`) by switching to bulk submission/evidence creation and skipping per-record auto-status sync/notification side effects during seed generation, reducing runtime for large financial years. |
| 2026-05-14 | Added staged progress checkpoints for demo seed loading: periodic in-session progress notifications plus chunked create batches so large runs provide visible progress and avoid long silent waits. |
| 2026-05-14 | Added environment-tunable demo seed performance controls via `ir.config_parameter`: `opms_ecdhs.demo_seed_chunk_size`, `opms_ecdhs.demo_seed_prep_notify_step`, and `opms_ecdhs.demo_seed_create_notify_every_chunks` (with safe min/max bounds). |
| 2026-05-14 | Optimized APP Matrix manual/auto import by caching repeated hierarchy upserts within a run and batching `opms.import.history.line` writes, reducing ORM round-trips and row-by-row write overhead for large Excel imports. |
| 2026-05-14 | Added staged progress notifications and tuning controls for APP Matrix manual/auto import (`opms_ecdhs.app_import_notify_step`, `opms_ecdhs.app_import_history_batch_size`) and optimized `copy_previous` by preloading target/source mappings and reducing repeated searches in plan/annual/quarterly copy loops. |
| 2026-05-14 | Added Import Performance controls to the OPMS Settings UI so admins can manage APP import, copy-previous, and demo-seed tuning values without editing `ir.config_parameter` manually. |
| 2026-05-14 | **New Option 3 — Load Demo APP Plans**: added full cascading hierarchy generator that creates APP Plan → Programme → Sub-Programme → Directorate → Output → Output Indicator → Annual Target → Quarters → Quarterly Targets with randomised planned target values. Indicator source is configurable: URL to APP/AOP PDF (downloaded + text extracted), local file path, uploaded PDF, bundled KPI Excel, or built-in 24-indicator fallback set. Old Option 3 (Load Demo Submissions) renumbered to **Option 4**. |
| 2026-05-14 | **Bug fix — versioned Excel creation**: `_next_versioned_filename` no longer raises `FileNotFoundError` when the `/data/` directory is absent (OSError caught, falls back to empty list); `action_auto_import_from_excel` now calls `os.makedirs(data_dir, exist_ok=True)` before writing the versioned file and wraps the write in `try/except OSError` with a graceful fallback so the import still proceeds when the directory is not writable. |
| 2026-05-14 | **New `standalone` aggregation rule** added (`Per Period / Non-Cumulative`): for indicators where each quarter is evaluated against the same target independently rather than accumulating. At the annual aggregation level, resolves to `average` (number/percentage), `all` (boolean), or `latest` (date/milestone/text). Added `standalone`, `per period`, `non-cumulative`, `non cumulative`, `independent` as recognised import aliases. Also improved `_infer_aggregation_rule` to return `average` for `number of days` / `days to` patterns. |

---

*Keep this file updated on every code or data change. Add a row to the Change Log with the date and a brief summary.*

Here's exactly how the system determines those Output Indicator field values:

## 1. **Measurement Type**
- **Initial default**: `"number"` (when creating a new indicator)
- **User-selected** from these options:
  - Number
  - Percentage
  - Date
  - Yes/No (Boolean)
  - Milestone
  - Text

## 2. **Aggregation Rule**
- **Initial default**: `"sum"`
- **Automatically set based on Measurement Type**: When you set the measurement type on an indicator, the system decides the aggregation rule:

| Measurement Type | Auto Aggregation Rule |
|---|---|
| **Number** | Sum |
| **Percentage** | Average |
| **Date** | Latest Submission |
| **Yes/No (Boolean)** | Latest Submission |
| **Milestone** | Latest Submission |
| **Text** | Latest Submission |

The actual logic is in this mapping (lines 185–194 of opms_models.py):
```python
def _default_aggregation_rule(measurement_type):
    defaults = {
        "number": "sum",
        "percentage": "average",
        "date": "latest",
        "boolean": "latest",
        "milestone": "latest",
        "text": "latest",
    }
    return defaults.get(measurement_type or "text", "latest")
```

## 3. **Comparison Direction**
- **Initial default**: `"higher"` (when creating a new indicator)
- **Automatically set based on Measurement Type**: The system decides how to compare planned vs. actual:

| Measurement Type | Auto Comparison Direction |
|---|---|
| **Number** | Higher is Better |
| **Percentage** | Higher is Better |
| **Date** | Lower is Better |
| **Yes/No (Boolean)** | Exact Match |
| **Milestone** | Exact Match |
| **Text** | Exact Match |

The actual logic is in this mapping (lines 197–206 of opms_models.py):
```python
def _default_comparison_direction(measurement_type):
    defaults = {
        "number": "higher",
        "percentage": "higher",
        "date": "lower",
        "boolean": "exact",
        "milestone": "exact",
        "text": "exact",
    }
    return defaults.get(measurement_type or "text", "exact")
```

## **Auto-Population Logic**
When you **create** or **update** an Output Indicator:
- If you **change the Measurement Type**, the system automatically recalculates Aggregation Rule and Comparison Direction (unless you explicitly override them in the same edit).
- See the model's `create()` and `write()` methods (lines 667–676 of opms_models.py).

This ensures consistency: a Date indicator always uses "Latest" aggregation and "Lower is Better" comparison by default, because dates are typically about deadlines or milestones where earlier is better.

==========================
BUT I AM DOING AN IMPORT NOT MANUALLY UPDATING INDICATORS, SO HOW DOES THE IMPORT KNOW WHAT TO TAG BECUASE ALSO ON THE EXCEL FILE, THERE ARE NO FIELDS/COLUUMNS TO SPECIFY THESE 3 FIELDS
==========================
I'll check the import wizard to see how it creates indicators and assigns these values when there's no explicit Excel column for them.

Searched for regex `output_indicator|measurement_type|aggregation_rule|comparison_direction` (`opms_ecdhs` · `wizard/opms_app_import_wizard.py`), 20 results

Read [](file:///Users/benjaminmaimba/Documents/GitHub/ECDHS-main/opms_ecdhs/wizard/opms_app_import_wizard.py#1-1), lines 1 to 100

Perfect! Now I see it. The import wizard has **inference logic** to automatically determine these values. Let me show you the full logic:

Read [](file:///Users/benjaminmaimba/Documents/GitHub/ECDHS-main/opms_ecdhs/wizard/opms_app_import_wizard.py#219-219), lines 219 to 320

Excellent question! The import wizard has **smart inference logic** to automatically determine these 3 fields since they're not in the Excel file. Here's exactly how it works:

## **1. Measurement Type Inference**
The system looks at (in order):

1. **Explicit column** (if provided) — uses Excel value
2. **Target values** — checks if annual/quarterly targets look like dates
3. **Indicator name** — pattern matches text:
   - Contains `"date"`, `"deadline"`, `"timeline"`, `"prescribed timelines"` → **Date**
   - Contains `"%"` or `"percentage"`, `"percent"` → **Percentage**
   - Contains `"achieved"`, `"compliant"`, `"approved"`, `"completed"`, `"implemented"` (but NOT "number of") → **Boolean (Yes/No)**
   - Contains `"milestone"` or `"submission of"` or `"tabling of"` (but NOT "number of") → **Milestone**
   - **Default** → **Number**

**Example**: `"Date of submission of MTEF Budget"` → infers **Date** because it matches `"date"` AND `"submission of"` patterns.

---

## **2. Aggregation Rule Inference**
Then based on the inferred Measurement Type + indicator name:

| Measurement Type | Auto Aggregation |
|---|---|
| **Percentage** | Average |
| **Date** | Latest |
| **Boolean** | Latest |
| **Milestone** | Latest |
| **Text** | Latest |
| **Number** (with turnaround/average/mean in name) | Average |
| **Number** (default) | Sum |

**Example**: `"Turnaround time to award a bid (120 days)"` → infers **Date** measurement type, then **Latest** aggregation (because dates use latest), AND **Lower is Better** direction (because time targets want minimal turnaround).

---

## **3. Comparison Direction Inference**
Based on Measurement Type + indicator name patterns:

| Measurement Type | Special Name Patterns | Result |
|---|---|---|
| **Date** | — | **Lower is Better** (earlier dates are better) |
| **Boolean/Milestone/Text** | — | **Exact Match** |
| **Number** | Contains `"turnaround"`, `"days to"`, `"average days"`, `"time to"` | **Lower is Better** |
| **Number** | (default) | **Higher is Better** |

---

## **The Complete Aliases Mapping** (from the import wizard)

If the Excel file **does** have explicit columns for these values, the import recognizes variations:

```
MEASUREMENT_TYPE: "number", "numeric", "percentage", "percent", "%", "date", "deadline", "boolean", "yes/no", "bool", "milestone", "text"

AGGREGATION_RULE: "sum", "count", "latest", "max", "maximum", "min", "minimum", "average", "avg", "any", "all"

COMPARISON_DIRECTION: "higher", "higher is better", "lower", "lower is better", "exact", "exact match"
```

So if your Excel had a hidden column with `"avg"`, the import would convert it to `"average"` aggregation rule.

---

## **Bottom Line**
The import wizard is **intelligent**: it reads only the indicator name and target values, then infers the 3 fields using pattern matching rules. This is why an indicator named `"Turnaround time to respond to Parliamentary findings"` automatically becomes:
- Measurement Type: **Date** (contains "time")
- Aggregation Rule: **Latest** (date auto-rule)
- Comparison Direction: **Lower is Better** (contains "turnaround time")

If you want **explicit control** over these values during import, you'd need to add optional columns to your Excel template that the wizard can read. Would you like me to add that capability?