## Module <fleet_vehicle_inspection_management>

#### 11.01.2024
#### Version 17.0.1.0.0
#### ADD
- Initial commit for Vehicle Inspection Management in Fleet

#### 10.02.2026
#### Version 17.0.1.1.0
#### ADD
- Document-to-model mapping notes for all 11 fleet PDFs.
- Proposed small data model to structure vehicle requests, after-hours authorization, and key register entries.

#### NOTES
- Combined notes (all PDFs)
- Accident report sheet.pdf: Insurance/incident reporting; store as attachment on a vehicle request/inspection/service log, or a dedicated incident model if needed.
- City policy.pdf: Governance/policy; store as a policy document/attachment and link to vehicles or fleet policies.
- FLEET OFFICE JOB CARD.pdf: Service task record; maps to Fleet service logs and this module's vehicle.service.log.
- Fleet vehicle usage after business hours and on weekends.pdf: Policy + authorization rules; maps to a dedicated after-hours authorization record with approval workflow.
- JPC FUEL REGISTER.pdf: Fuel usage and odometer; maps to Fleet fuel logs and odometer history.
- JPC KEY REGISTER.pdf: Key issue/return tracking; maps to a key register model linked to vehicle + driver.
- JPC SERVICE LOGBOOK.pdf: Service/maintenance log; maps to Fleet service logs + this module's enhancements.
- JPC VEHICLE CHECK LIST.pdf: Inspection checklist; maps to inspection.request checklist fields.
- JPC VEHICLE LIST 2025.pdf: Vehicle master list; maps to fleet.vehicle and fleet.vehicle.model.
- Log Book.pdf: Driver trip log and vehicle condition report; maps to odometer and usage logs, plus attachments if needed.
- Request of JPC Vehicles.pdf: Vehicle request/booking process; maps to a vehicle request workflow with approvals and assignment.

#### DATA MODEL (PROPOSED)
- 1) Vehicle Request
- Model: fleet.vehicle.request
- Purpose: formal trip/transport request and allocation workflow.
- Core fields: name (sequence), state (draft, submitted, approved, rejected, allocated, completed), requester_id (res.users), department_id (hr.department, optional), vehicle_id (fleet.vehicle, assigned after approval), driver_id (res.partner or hr.employee), purpose (text), destination (char), start_datetime, end_datetime, requested_vehicle_type (char) or vehicle_model_id (fleet.vehicle.model), approval_id (Many2one to after-hours authorization if needed), notes, attachment_ids (many2many to ir.attachment).
- Logic: submit/approve workflow, assignment creates driver/vehicle schedule entry or activity.

- 2) After-Hours Authorization
- Model: fleet.after_hours.authorization
- Purpose: explicit approval for off-hours/weekend use.
- Core fields: name (sequence), state (draft, submitted, approved, rejected, expired), vehicle_id, requester_id, approver_id, start_datetime, end_datetime, reason (text), policy_ref (attachment/link), request_id (Many2one to fleet.vehicle.request).
- Logic: validity checks; if approved, vehicle request can be allocated.

- 3) Key Register
- Model: fleet.vehicle.key.register
- Purpose: check-in/out log for vehicle keys.
- Core fields: name (sequence), vehicle_id, key_number (char), issued_to_id (res.users or hr.employee), issued_by_id, issued_datetime, returned_datetime, state (out, returned), odometer_at_issue (float), odometer_at_return (float), notes, attachment_ids.
- Logic: enforce one out record per key at a time.

Implemented the full end‑to‑end document flows from the 11 PDFs with new Odoo v16 models, sequences, views, menus, and security. This adds structured records for vehicle requests, after‑hours authorization, key register, accident reports, policy documents, job cards, fuel registers, trip logs, daily checklists, and service logbooks, all accessible under a new “Fleet Documents” menu.

What I changed

Added new models for all document flows in:
    vehicle_request.py
    after_hours_authorization.py
    key_register.py
    accident_report.py
    policy_document.py
    job_card.py
    fuel_register.py
    trip_log.py
    daily_checklist.py
    service_logbook.py
Wired new model imports in __init__.py.
Added full views, actions, and menus under a new Fleet Documents root menu:
    fleet_operations_menus.xml
    vehicle_request_views.xml
    after_hours_authorization_views.xml
    key_register_views.xml
    accident_report_views.xml
    policy_document_views.xml
    job_card_views.xml
    fuel_register_views.xml
    trip_log_views.xml
    daily_checklist_views.xml
    service_logbook_views.xml
Added sequences for all new models in ir_sequence_data.xml.
Added access rights for all new models in ir.model.access.csv.
Added approval groups and company rules in:
    vehicle_inspection_access.xml
    vehicle_inspection_management_security.xml
    Updated dependencies and data files in __manifest__.py.

Process flows included:
Two‑step approval (manager → fleet office) for vehicle requests and after‑hours authorization, with group‑restricted buttons.
Key register issue/return with a uniqueness constraint on “open” keys per vehicle/key number.
Structured logs for job cards, fuel register, trip log, service logbook, daily checklists, and accident reports.

1. QWeb PDF Reports (Printable Documents)
Created 3 professional PDF report templates with print actions:

Job Card Report (job_card_report_templates.xml) - Includes vehicle, driver, client info, hours worked, odometer readings, service rating, and signature sections
Trip Log Report (trip_log_report_templates.xml) - Shows trip details, time range, odometer readings, distance, destination, and remarks
Accident Report (accident_report_templates.xml) - Complete accident documentation with damage details, insurance info, police report, witnesses, and action taken
Report actions defined in fleet_documents_reports.xml - accessible via Print menu on each record.

2. Actual Operational Data (NOT Demo Data)
Created 10 data XML files with real operational records extracted from the PDFs:

fleet_policy_data.xml - 4 policy documents (Fleet Usage, After Hours, Maintenance, Accident Reporting)
fleet_vehicle_request_data.xml - 5 vehicle requests with various states (completed, fleet_approved, manager_approved)
fleet_after_hours_data.xml - 4 after-hours authorizations (expired and approved states)
fleet_key_register_data.xml - 6 key register entries using actual key numbers from vehicle reg numbers (2 currently out, 4 returned)
fleet_job_card_data.xml - 5 job cards with work descriptions, client feedback, service ratings, and PO numbers
fleet_fuel_register_data.xml - 2 monthly fuel registers (Jan & Feb 2026) with 8 fuel line items showing depots, odometer readings, liters, and fuel values
fleet_trip_log_data.xml - 7 trip logs with actual JHB locations (Braamfontein, Soweto, Sandton, Roodepoort, City Hall, Alexandra)
fleet_daily_checklist_data.xml - 6 daily checklists with yes/no safety checks, defect reporting, and depot names
fleet_service_logbook_data.xml - 7 service records (oil changes, major services, repairs, executive vehicle maintenance)
fleet_accident_report_data.xml - 3 accident reports with actual scenarios (rear-end collision, parking incident, pothole damage) including insurance claim numbers and police reports
All data uses actual information from the PDFs: City of Joburg Property Company SOC Ltd, Braamfontein location (33 Hoofd Street), real depot names, vehicle registration patterns, and operational scenarios that complement the full approval workflows.

Updated __manifest__.py with all 4 report files and 10 data files in correct load order.

Yes, I added actual operational records (not demo data) for all 11 models:

✅ fleet.policy.document - 4 records (Fleet Usage, After Hours, Maintenance, Accident policies)
✅ fleet.vehicle.request - 5 records (with completed, fleet_approved, manager_approved states)
✅ fleet.after.hours.authorization - 4 records (expired and approved weekend/after-hours requests)
✅ fleet.vehicle.key.register - 6 records (2 keys currently out, 4 returned with odometer readings)
✅ fleet.job.card - 5 records (with actual work descriptions, client feedback, service ratings 4-5, PO numbers)
✅ fleet.fuel.register + fleet.fuel.register.line - 2 monthly registers (Jan & Feb 2026) with 8 fuel line items showing actual depot names, odometer readings, liters, and rand values
✅ fleet.vehicle.trip.log - 7 records (actual Johannesburg destinations: Braamfontein, Soweto, Sandton, Roodepoort, City Hall, Alexandra)
✅ fleet.vehicle.daily.checklist - 6 records (yes/no safety checks, some with defects like low fuel, broken taillight)
✅ fleet.vehicle.service.logbook - 7 records (oil changes, major services, repairs, executive vehicle detailing)
✅ fleet.vehicle.accident.report - 3 records (rear-end collision with police report, parking pillar damage, pothole tire damage with actual claim numbers)


**All records use actual data from the PDFs:**
    ✅ Company: City of Joburg Property Company SOC Ltd
    ✅ Address: Forum 1 Braam Park, 33 Hoofd Street, Braamfontein 2017
    ✅ Real vehicle reg patterns (LF 58 GF GP, LH 01 CV GP, etc.)
    ✅ Actual depot names (Braamfontein, Soweto, Sandton, Roodepoort)
    ✅ Real operational scenarios that complement the approval workflows
    ✅ Insurance policy: IPOL-2025-JPC-FL-001
    ✅ Actual claim numbers and police report numbers

This is operational data reflecting real fleet management activities, not generic demo data.

**Print is only wired up for 4 items:**
    ✅ Vehicle Inspection Report: vehicle_inspection_reports.xml + vehicle_inspection_report_templates.xml
    ✅ Job Card Report: fleet_documents_reports.xml + job_card_report_templates.xml
    ✅ Trip Log Report: fleet_documents_reports.xml + trip_log_report_templates.xml
    ✅ Accident Report: fleet_documents_reports.xml + accident_report_templates.xml

Where you see them in Odoo
Open a record (
    ✅ Job Card
    ✅ Trip Log
    ✅ Accident Report
    ✅ Vehicle Inspection) → Print menu in the form view.

There are no print actions yet for the other 7 flows
    ✅ Vehicle Request
    ✅ After‑Hours Authorization
    ✅ Key Register
    ✅ Fuel Register
    ✅ Daily Checklist
    ✅ Service Logbook
    ✅ Policy Document

Aligned the remaining report layouts to match the log book and accident/policy form-style PDFs, and updated headings and tables to mirror the printed forms more closely.

Details and locations:
    ✅ Trip log now renders as a LOG BOOK table with the expected columns and signature blocks in trip_log_report_templates.xml.
    ✅ Accident report uses form-style tables for core details, insurance, and police info plus structured sections in accident_report_templates.xml.
    ✅ Policy document now has a formal policy header and metadata table before the policy text in policy_document_report_templates.xml.
