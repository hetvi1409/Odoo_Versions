# Enhanced Fleet Management - Documents & Requirements

## Overview

The Enhanced Fleet Management module for Odoo 18 digitizes and automates all fleet management processes for the Department of Human Settlements. This document outlines the document requirements, PDF form integration, and technical dependencies.

## PDF Documents Integrated

This module implements requirements from the following 11 official PDF documents:

### 1. Transport_request_form.pdf
**Purpose:** Employee transport request submission
**Integration:** `fleet.transport.request` model
**Key Fields:**
- Requester information (name, department, contact)
- Trip details (date, time, destination, purpose)
- Passenger count and special requirements
- Department manager approval
- Fleet manager approval and vehicle assignment

### 2. Trip_authority_Form.pdf
**Purpose:** Official trip authorization and tracking
**Integration:** `fleet.trip.authority` model
**Key Fields:**
- Employee and vehicle assignment
- Driver details
- Trip schedule (departure/return dates)
- Route and destination
- Authorization signatures
- Pre/post-trip checklist references
- Odometer readings (start/end)
- Fuel tracking

### 3. MANUAL_TRIP_AUTHORISATION_2018.pdf
**Purpose:** Sequential trip register and tracking
**Integration:** Trip numbering system
**Key Fields:**
- Sequential trip numbers (format: GGG145776/01/2024)
- Registration number
- Trip date
- Mileage tracking
- Trip history preservation

### 4. Vehicle_checklist_form.pdf
**Purpose:** Comprehensive vehicle inspection
**Integration:** `fleet.vehicle.checklist` model
**Key Fields:**
- Inspection type (pre-trip, post-trip, scheduled, random)
- Exterior checks (body, lights, mirrors, tyres)
- Under hood checks (fluids, battery, leaks)
- Interior checks (seats, seatbelts, instruments)
- Safety equipment (fire extinguisher, first aid, warning triangle)
- Documents verification (license disc, registration, insurance)
- Roadworthiness assessment
- Inspector signature and driver acknowledgment

### 5. Checklist_for_accidents.pdf
**Purpose:** Accident reporting and documentation
**Integration:** `fleet.accident.report` model
**Key Fields:**
- Accident details (date, time, location, conditions)
- Vehicle and driver information
- Third-party details
- Witness information
- Damage assessment
- Police report details
- Insurance claim information
- Investigation findings

### 6. RT46_accident_form.pdf
**Purpose:** Official accident report form (regulatory compliance)
**Integration:** `fleet.accident.report` model (RT46 section)
**Key Fields:**
- Official accident report number
- Regulatory compliance fields
- Police case/docket number
- Investigating officer details
- Formal accident description
- Fault determination

### 7. Checklist_for_lost_and_theft_Form.pdf
**Purpose:** Lost, theft, and hijacking incident reporting
**Integration:** `fleet.lost.theft` model
**Key Fields:**
- Incident type (theft, loss, hijacking, burglary, vandalism)
- Vehicle details
- Incident date/time and discovery date/time
- Location and last known position
- Keys and documents status
- Tracking device status
- Police report (case number)
- Insurance claim (claim number)
- Recovery details
- Investigation findings

### 8. GFMS_Vehicle_relief_form.pdf
**Purpose:** Vehicle relief/replacement management
**Integration:** `fleet.vehicle.relief` model
**Key Fields:**
- Original vehicle details
- Relief vehicle details
- Relief reason (maintenance, repair, accident, breakdown)
- Expected duration
- Handover checklist
- Return checklist
- Cost tracking

### 9. FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf
**Purpose:** Complete vehicle register and fleet management
**Integration:** `fleet.vehicle` model extensions
**Key Fields:**
- Vehicle categories (1, 5, 6, 11, 15, MM)
- Registration number
- Description (make/model)
- Chassis and engine numbers
- Date received
- Section/department assignment
- Driver assignment
- Accessories (radio, aircon, canopy)
- License renewal date
- Maintenance type (FML, MM)
- Contract term (60 months, 120,000 KM)
- Monthly cost (R6,684.82 - R13,459.09 for FML, R1,232.45 for MM)
- Cost center allocation

### 10. Human_Settlements_Odo_metres.pdf
**Purpose:** Odometer tracking and vehicle usage history
**Integration:** `fleet.odometer.reading` model
**Key Fields:**
- Odometer readings over time
- Vehicle replacement history
- Usage tracking
- Distance calculations
- Fuel level monitoring
- Reading verification

### 11. TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf
**Purpose:** Service and maintenance tracking
**Integration:** `fleet.vehicle.log.services` extensions
**Key Fields:**
- Work order numbers (WO format)
- Service dates (start/completion)
- Vehicle and driver details
- Service provider information
- Service type
- Cost tracking
- Invoice management
- Service history

## Vehicle Categories

Based on FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf, the system supports:

### Category 1: Sedans
- VW Polo Vivo
- Toyota Etios
- Nissan Almera
- Hyundai Grand i10

### Category 5: LDV 4x2 1 ton
- Isuzu D-MAX
- Toyota Hilux
- Ford Ranger

### Category 6: LDV 4x2 D/Cab
- Isuzu D-MAX

### Category 11: LDV 4x4 1 ton light
- Toyota Hilux
- Isuzu D-MAX

### Category 15: 16 Seater
- VW Crafter

### MM Vehicles: Ministerial
- Audi Q7
- BMW X4

## Maintenance Contract Types

### FML (Full Maintenance Lease)
- **Term:** 60 months
- **Cost Range:** R6,684.82 to R13,459.09 per month
- **Coverage:** Full maintenance and service
- **Providers:** Various contracted service providers

### MM (Ministerial Maintenance)
- **Coverage:** 120,000 KM
- **Cost:** R1,232.45 per month
- **Special:** Ministerial vehicle maintenance

## Document Workflows

### Transport Request Workflow
1. **Draft** → Employee creates request
2. **Submitted** → Request sent for approval
3. **Approved** → Department Manager approves
4. **Vehicle Assigned** → Fleet Manager assigns vehicle and driver
5. **In Progress** → Trip commences
6. **Completed** → Trip finished and documented

### Trip Authority Workflow
1. **Draft** → Auto-generated from approved transport request
2. **Issued** → Fleet Manager issues authority
3. **Active** → Driver activates trip
4. **Completed** → Trip finished with all documentation

### Vehicle Checklist Workflow
1. **Draft** → Checklist created
2. **In Progress** → Inspection being performed
3. **Completed** → Inspection finished
4. **Approved** → Fleet Manager approves

### Accident Report Workflow
1. **Draft** → Accident reported
2. **Reported** → Initial report submitted
3. **Under Investigation** → Investigation in progress
4. **Police Reported** → Police case opened
5. **Insurance Claimed** → Insurance claim submitted
6. **Resolved** → Case closed

### Lost & Theft Workflow
1. **Draft** → Incident reported
2. **Reported** → Initial report submitted
3. **Under Investigation** → Investigation in progress
4. **Police Reported** → Police case opened
5. **Insurance Claimed** → Insurance claim submitted
6. **Recovered** → Vehicle recovered (if applicable)
7. **Resolved** → Case closed

### Vehicle Relief Workflow
1. **Draft** → Relief request created
2. **Submitted** → Request sent for approval
3. **Approved** → Fleet Manager approves
4. **Vehicle Assigned** → Relief vehicle assigned
5. **Active** → Relief period active
6. **Completed** → Original vehicle returned

## Required Documents per Process

### Transport Request
- Transport request form (PDF)
- Department manager approval
- Fleet manager approval
- Vehicle assignment confirmation

### Trip Authority
- Trip authority form (PDF)
- Pre-trip checklist
- Post-trip checklist
- Fuel receipts
- Trip report
- Odometer readings

### Vehicle Inspection
- Vehicle checklist form (PDF)
- Photos of any damage
- Inspector signature
- Driver acknowledgment
- Maintenance work order (if issues found)

### Accident Reporting
- Accident report form (PDF)
- RT46 form (PDF)
- Police report (case/docket number)
- Photos of damage
- Witness statements
- Insurance claim documents
- Repair estimates
- Investigation report

### Lost & Theft Reporting
- Lost & theft report form (PDF)
- Police report (case number)
- Insurance claim documents
- Tracking device reports
- Keys accountability declaration
- Recovery documentation (if applicable)
- Investigation report

### Vehicle Relief
- Vehicle relief form (PDF)
- Handover checklist
- Return checklist
- Relief period documentation
- Cost allocation

### Service & Maintenance
- Work order (PDF)
- Service report
- Invoice
- Parts list
- Quality inspection report
- Service history update

## Technical Dependencies

### Odoo Modules
- **base** - Core Odoo functionality
- **fleet** - Fleet management base
- **hr** - Human resources (employee data)
- **mail** - Email notifications and activity tracking
- **web** - Web interface

### Optional Modules
- **documents** - Document management (Enterprise)
- **documents_fleet** - Fleet document integration (Enterprise)

### Python Dependencies
- Python 3.10+
- Standard Odoo 18 dependencies

## Documents Module Integration

### Issue
If you see an error: **"res.config.settings"."documents_fleet_folder" field is undefined"**

### Solution
This error occurs when you have the Enterprise `documents_fleet` module installed but the base `documents` module is not installed.

#### To Fix:
1. Go to **Apps** in Odoo (http://localhost:18000/web#action=base.open_module_tree)
2. Remove the **"Apps"** filter to show all modules
3. Search for **"Documents"**
4. Click **Install** on the "Documents" module (NOT documents_fleet)
5. Wait for installation to complete
6. Restart your Odoo server
7. Upgrade the Enhanced Fleet Management module

#### Alternative Solution:
If you don't need the Documents integration:
1. Go to **Apps**
2. Search for **"Fleet"**
3. Find **"Documents - Fleet"** (documents_fleet)
4. Click **Uninstall**

### Technical Details
The `enhanced_fleet_management` module defines the `documents_fleet_settings` and `documents_fleet_folder` fields to maintain compatibility with the Enterprise `documents_fleet` module. These fields require the `documents.folder` model to exist, which is provided by the base `documents` module.

## Data Migration

### Importing Historical Data

#### Fleet Register Import
```python
# Import vehicle data from FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf
# Preserve vehicle categories, maintenance contracts, cost centers
```

#### Trip History Import
```python
# Import trip data from MANUAL_TRIP_AUTHORISATION_2018.pdf
# Preserve odometer readings, trip numbers, sequential numbering
```

#### Service History Import
```python
# Import service records from TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf
# Preserve work order numbers, costs, service provider details
```

#### Odometer History Import
```python
# Import odometer data from Human_Settlements_Odo_metres.pdf
# Preserve vehicle replacement history, usage tracking data
```

## Compliance Requirements

### Record Retention
- **Transport Requests:** 3 years
- **Trip Authorities:** 3 years
- **Vehicle Checklists:** 5 years
- **Lost/Theft Reports:** 7 years
- **Accident Reports:** 7 years
- **Maintenance Records:** Vehicle lifetime
- **Service Invoices:** 7 years

### Audit Trail
- All state changes logged with timestamp and user
- User actions tracked
- Approval chain maintained
- Document versions preserved
- Odometer history maintained
- Cost tracking complete

### Regulatory Compliance
- RT46 form compliance for accidents
- Police reporting for theft/hijacking
- Insurance claim documentation
- License disc renewal tracking
- Safety equipment verification
- Maintenance record keeping
- Driver qualification tracking

## Security & Access Control

### Role-Based Access
- **Fleet User:** Create requests, view own records, report incidents
- **Fleet Manager:** Approve requests, assign vehicles, investigate incidents
- **Fleet Administrator:** Full system access, configuration, master data

### Record-Level Security
- Department-based visibility
- Manager approval requirements
- Audit logging
- Data integrity protection

## Reporting Requirements

### Standard Reports
1. Transport Request Form (PDF)
2. Trip Authority Form (PDF)
3. Vehicle Checklist Form (PDF)
4. Accident Report (RT46) (PDF)
5. Lost & Theft Report (PDF)
6. Vehicle Relief Form (PDF)
7. Trip Register Report (PDF)
8. Fleet Register Report (PDF)
9. Service History Report (PDF)

### Analytics Reports
- Fleet utilization analysis
- Maintenance cost tracking
- Incident statistics
- Trip frequency analysis
- Fuel consumption tracking
- Vehicle condition trends
- Driver performance metrics

## Best Practices

### Document Management
- Attach all supporting documents to records
- Maintain photo evidence for incidents
- Keep fuel receipts for all trips
- Preserve service invoices
- Archive completed records

### Data Quality
- Ensure accurate odometer readings
- Verify vehicle information
- Complete all required fields
- Provide detailed descriptions
- Update records promptly

### Workflow Compliance
- Follow approval hierarchies
- Complete checklists thoroughly
- Report incidents immediately
- Submit trip reports on time
- Maintain audit trail

## Support & Maintenance

### Regular Tasks
- **Daily:** Monitor pending requests and active trips
- **Weekly:** Review pending requests and overdue trips
- **Monthly:** Analyze fleet utilization and maintenance schedules
- **Quarterly:** Review incident statistics and costs
- **Annually:** Update forms, review contracts, plan replacements

### System Health
- Monitor checklist completion rates
- Track average approval times
- Review incident trends
- Analyze vehicle condition scores
- Monitor maintenance costs

## Future Enhancements

### Planned Features
1. Mobile app for checklist completion
2. GPS integration for real-time tracking
3. Fuel card integration
4. Predictive maintenance alerts
5. Advanced analytics dashboard
6. Driver performance scoring
7. Automated scheduling optimization
8. Integration with telematics systems

---

**Document Version:** 2.0.0
**Last Updated:** January 2026
**Module Version:** 18.0.2.0.0
**Author:** ECDHS
**Organization:** Department of Human Settlements

For detailed process flows, see [PROCESS_FLOW.md](PROCESS_FLOW.md)
For PDF analysis, see [PDF_ANALYSIS_SUMMARY.md](PDF_ANALYSIS_SUMMARY.md)
For implementation details, see [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
