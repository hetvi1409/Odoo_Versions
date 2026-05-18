# Enhanced Fleet Management Module - Process Flow Documentation

## Overview
The Enhanced Fleet Management module for Odoo 18 provides comprehensive fleet operations management with integrated forms for transport requests, trip authorities, vehicle inspections, and incident reporting. This module is specifically designed for the Department of Human Settlements and incorporates all requirements from the official PDF forms and documents.

## Module Information
- **Module Name:** enhanced_fleet_management
- **Version:** 18.0.1.0.0
- **Category:** Human Resources/Fleet
- **Dependencies:** base, fleet, hr, mail, web
- **Target Organization:** Department of Human Settlements
- **Compliance:** Aligned with FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf and all official forms

## Vehicle Categories (From Fleet Register)

The system supports the following vehicle categories as per the Department of Human Settlements Fleet Register:

- **Category 1:** Sedans (VW Polo Vivo, Toyota Etios, Nissan Almera, Hyundai Grand i10)
- **Category 5:** LDV 4x2 1 ton (Isuzu D-MAX, Toyota Hilux, Ford Ranger)
- **Category 6:** LDV 4x2 D/Cab (Isuzu D-MAX)
- **Category 11:** LDV 4x4 1 ton light (Toyota Hilux, Isuzu D-MAX)
- **Category 15:** 16 Seater (VW Crafter)
- **MM Vehicles:** Ministerial vehicles (Audi Q7, BMW X4)

## Maintenance Contract Types

- **FML (Full Maintenance Lease):** 60 months standard term
  - Cost range: R6,684.82 to R13,459.09 per month
- **MM (Ministerial Maintenance):** 120,000 KM coverage
  - Cost: R1,232.45 per month

## Process Flows

### 1. Transport Request Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSPORT REQUEST WORKFLOW                    │
│              (Based on Transport_request_form.pdf)               │
└─────────────────────────────────────────────────────────────────┘

[EMPLOYEE]
    │
    ├─► Creates Transport Request (Draft)
    │   • Fills requester information (Name, Department, Contact)
    │   • Specifies trip details (date, time, destination)
    │   • Provides purpose and passenger information
    │   • Marks urgency if applicable
    │   • Indicates special requirements
    │
    ├─► Submits Request (Submitted)
    │   • Auto-notifies Department Manager
    │   • Request locked for editing
    │   • Request number generated (TR#####)
    │
    ↓

[DEPARTMENT MANAGER]
    │
    ├─► Reviews Request
    │   • Verifies business justification
    │   • Checks budget approval
    │   • Validates passenger count
    │   • Adds manager comments
    │
    ├─► Approves/Rejects (Approved)
    │   • Auto-notifies Fleet Manager
    │   • If rejected: Returns to draft or cancelled
    │   • Approval timestamp recorded
    │
    ↓

[FLEET MANAGER]
    │
    ├─► Reviews Approved Request
    │   • Checks vehicle availability by category
    │   • Verifies vehicle maintenance status
    │   • Assigns appropriate vehicle
    │   • Assigns qualified driver
    │   • Adds fleet manager comments
    │
    ├─► Final Approval (Vehicle Assigned)
    │   • Auto-creates Trip Authority
    │   • Generates Trip Number (Sequential: GGG145776/01/2024 format)
    │   • Notifies employee and driver
    │   • Trip Authority issued
    │   • Pre-trip checklist auto-created
    │
    ↓

[DRIVER/EMPLOYEE]
    │
    ├─► Trip Commences (In Progress)
    │   • Pre-trip checklist completed
    │   • Starting odometer reading recorded
    │   • Fuel level noted
    │   • Passenger list confirmed
    │
    ├─► Trip Execution
    │   • Vehicle used for authorized purpose
    │   • Any incidents reported immediately
    │   • Fuel receipts collected
    │
    ├─► Trip Completion (Completed)
    │   • Post-trip checklist completed
    │   • Final odometer reading recorded
    │   • Fuel receipts submitted
    │   • Trip report provided
    │   • Mileage calculated automatically
    │
    └─► Archive

[CANCELLATION PATH]
    Any stage (except Completed) → Cancel
    • Reason for cancellation required
    • Notifications sent to all stakeholders
    • Vehicle assignment released
    • Trip authority cancelled
```

### 2. Trip Authority Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRIP AUTHORITY WORKFLOW                      │
│              (Based on Trip_authority_Form.pdf and               │
│           MANUAL_TRIP_AUTHORISATION_2018.pdf)                    │
└─────────────────────────────────────────────────────────────────┘

[AUTO-GENERATED from Approved Transport Request]
    │
    ├─► Trip Authority Created (Draft)
    │   • Employee information populated
    │   • Vehicle and driver assigned
    │   • Trip schedule defined
    │   • Purpose and destination set
    │   • Trip number generated (Sequential format)
    │   • Odometer reading initialized
    │
    ├─► Fleet Manager Issues Authority (Issued)
    │   • Authorization signature applied
    │   • Pre-trip checklist auto-created
    │   • Driver notified
    │   • Authority document printable
    │   • Trip number recorded in register
    │
    ↓

[PRE-TRIP INSPECTION]
    │
    ├─► Vehicle Checklist Completed
    │   • Inspector performs comprehensive check
    │   • All safety equipment verified
    │   • Vehicle condition assessed
    │   • Defects recorded if found
    │   • License disc validity checked
    │   • Insurance certificate verified
    │
    ├─► Roadworthy Decision
    │   • YES → Proceed with trip
    │   • NO → Vehicle replaced, new checklist
    │
    ↓

[TRIP ACTIVATION]
    │
    ├─► Driver Activates Trip (Active)
    │   • Records starting odometer (matches trip register)
    │   • Notes fuel level
    │   • Confirms passenger list
    │   • Emergency contact verified
    │   • Trip start time logged
    │
    ├─► During Trip
    │   • GPS tracking active (if equipped)
    │   • Any incidents reported immediately
    │   • Fuel purchases receipted
    │   • Odometer monitored
    │
    ↓

[TRIP COMPLETION]
    │
    ├─► Vehicle Returns
    │   • Records ending odometer
    │   • Notes final fuel level
    │   • Submits fuel receipts
    │   • Trip end time logged
    │   • Distance calculated (End - Start odometer)
    │
    ├─► Post-Trip Checklist
    │   • Comprehensive vehicle inspection
    │   • Any damage documented
    │   • Issues reported
    │   • Vehicle condition updated
    │
    ├─► Trip Report Submission
    │   • Summary of trip provided
    │   • Incidents explained
    │   • Recommendations noted
    │   • Fuel consumption calculated
    │
    ├─► Authority Completed
    │   • Transport request updated
    │   • All documentation archived
    │   • Trip register updated
    │   • Odometer history preserved
    │
    └─► Final Approval
        • Fleet manager reviews completion
        • Trip authority closed
        • Statistics updated
```

### 3. Vehicle Checklist Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  VEHICLE CHECKLIST WORKFLOW                      │
│              (Based on Vehicle_checklist_form.pdf)               │
└─────────────────────────────────────────────────────────────────┘

[INSPECTION TRIGGER]
    ├─► Pre-Trip (Before journey)
    ├─► Post-Trip (After journey)
    ├─► Scheduled (Regular maintenance)
    └─► Random (Spot checks)

[INSPECTION PROCESS]
    │
    ├─► Checklist Created (Draft)
    │   • Inspector assigned
    │   • Vehicle selected (with category)
    │   • Inspection type specified
    │   • Date and odometer recorded
    │   • Checklist number generated (VC#####)
    │
    ├─► Inspection Begins (In Progress)
    │
    ├─► EXTERIOR CHECKS
    │   • Body condition (dents, scratches, rust)
    │   • All lights (head, tail, indicators, brake, fog)
    │   • Mirrors (side and rear view)
    │   • Windows and windscreen
    │   • Windscreen wipers (front and rear)
    │   • All tyres including spare (tread depth, pressure)
    │   • License disc visible and valid
    │   • Registration plates secure
    │
    ├─► UNDER HOOD CHECKS
    │   • Engine oil level (dipstick check)
    │   • Coolant level (reservoir check)
    │   • Brake fluid level
    │   • Power steering fluid
    │   • Windscreen washer fluid
    │   • Battery condition (terminals, charge)
    │   • Check for leaks (oil, coolant, fuel)
    │   • Belts and hoses condition
    │
    ├─► INTERIOR CHECKS
    │   • Seats condition (tears, adjustments)
    │   • All seatbelts functional (all positions)
    │   • Dashboard instruments working
    │   • Horn operational
    │   • Air conditioning/heater functional
    │   • Interior lights (dome, reading)
    │   • Radio/sound system operational
    │   • Steering wheel condition
    │   • Pedals (brake, clutch, accelerator)
    │
    ├─► SAFETY EQUIPMENT
    │   • Fire extinguisher (valid, accessible)
    │   • First aid kit (complete, not expired)
    │   • Warning triangle (reflective)
    │   • Jack and wheel spanner
    │   • Reflective vest (high visibility)
    │   • Spare wheel (inflated, good condition)
    │
    ├─► DOCUMENTS CHECK
    │   • License disc (valid, displayed)
    │   • Vehicle registration papers
    │   • Insurance certificate (current)
    │   • Service book (up to date)
    │   • Roadworthy certificate (if applicable)
    │
    ├─► OVERALL ASSESSMENT
    │   • System auto-calculates condition score
    │   • Counts issues found by severity
    │   • Determines roadworthiness status
    │   • Generates recommendations
    │
    ├─► Inspection Completed
    │   • Defects Description provided
    │   • Recommendations made
    │   • Photos attached if needed
    │   • Inspector signature
    │   • Driver acknowledgment
    │   • Completion timestamp
    │
    ↓

[DECISION POINTS]
    │
    ├─► NO ISSUES (Excellent/Good)
    │   • Checklist approved
    │   • Vehicle cleared for use
    │   • Regular maintenance scheduled
    │   • Next inspection date set
    │
    ├─► MINOR ISSUES (Fair)
    │   • Issues documented
    │   • Maintenance requested
    │   • Vehicle usable with caution
    │   • Follow-up inspection scheduled
    │   • Driver notified of issues
    │
    ├─► MAJOR ISSUES (Poor)
    │   • Immediate maintenance required
    │   • Vehicle use restricted
    │   • Repairs prioritized
    │   • Re-inspection mandatory
    │   • Fleet manager notified
    │
    └─► UNSAFE
        • Vehicle grounded immediately
        • Alternative transport arranged
        • Urgent repairs commissioned
        • Safety incident logged
        • Senior management notified

[FOLLOW-UP ACTIONS]
    │
    ├─► Maintenance Work Order Created
    │   • Service provider assigned
    │   • Work order number generated
    │   • Cost estimate obtained
    │   • Repair timeline set
    │
    ├─► Fleet Manager Notified
    │   • Email notification sent
    │   • Dashboard alert created
    │   • Approval required for major repairs
    │
    ├─► Vehicle Status Updated
    │   • Availability status changed
    │   • Condition score updated
    │   • Maintenance flag set
    │
    └─► Inspection History Logged
        • Record archived
        • Statistics updated
        • Trend analysis data captured
```

### 4. Accident Reporting Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  ACCIDENT REPORTING WORKFLOW                     │
│         (Based on Checklist_for_accidents.pdf and                │
│                    RT46_accident_form.pdf)                       │
└─────────────────────────────────────────────────────────────────┘

[ACCIDENT OCCURRENCE]
    │
    ├─► Accident Happens
    │   • Ensure safety of all parties
    │   • Call emergency services if needed
    │   • Secure the scene
    │   • Take photos/videos
    │   • Exchange information with other parties
    │
    ↓

[IMMEDIATE RESPONSE]
    │
    ├─► Accident Report Created (Draft)
    │   • Reporter details captured
    │   • Vehicle information recorded
    │   • Accident date/time
    │   • Location details (GPS coordinates)
    │   • Weather and road conditions
    │   • Driver information
    │
    ├─► Detailed Documentation
    │   • Comprehensive accident description
    │   • Diagram of accident scene
    │   • Other vehicles involved
    │   • Third-party information
    │   • Witness details (names, contacts)
    │   • Photos/evidence uploaded
    │   • Driver statement
    │   • Passenger statements
    │
    ├─► Damage Assessment
    │   • Vehicle damage description
    │   • Damage severity rating
    │   • Estimated repair costs
    │   • Photos of all damage
    │   • Third-party damage (if any)
    │
    ├─► Submit Report (Reported)
    │   • Fleet manager auto-notified
    │   • Senior management alerted
    │   • Report locked for integrity
    │   • Report number generated
    │
    ↓

[INVESTIGATION PHASE]
    │
    ├─► Investigation Assigned (Under Investigation)
    │   • Investigation officer appointed
    │   • Initial assessment conducted
    │   • Evidence gathered
    │   • CCTV footage reviewed (if available)
    │   • Interviews conducted
    │   • Breathalyzer results (if applicable)
    │
    ├─► Fault Determination
    │   • Driver fault assessment
    │   • Third-party fault assessment
    │   • Contributing factors identified
    │   • Preventability analysis
    │
    ↓

[OFFICIAL REPORTING]
    │
    ├─► Police Report (Police Reported)
    │   • Case opened at police station
    │   • Case/docket number obtained
    │   • Investigating officer assigned
    │   • Statement provided
    │   • Police report copy attached
    │   • RT46 form completed
    │
    ├─► RT46 Form Submission
    │   • Official accident report form
    │   • Submitted to authorities
    │   • Compliance with regulations
    │   • Copy retained in system
    │
    ↓

[INSURANCE CLAIM]
    │
    ├─► Insurance Notification (Insurance Claimed)
    │   • Insurance company contacted
    │   • Claim number obtained
    │   • Required documents submitted:
    │     - Police report
    │     - RT46 form
    │     - Photos of damage
    │     - Witness statements
    │     - Driver's license copy
    │     - Vehicle registration
    │   • Insurance assessor assigned
    │
    ├─► Claim Processing
    │   • Assessor inspection
    │   • Damage valuation
    │   • Repair authorization
    │   • Claim status tracked
    │   • Settlement negotiation
    │
    ↓

[REPAIR & RECOVERY]
    │
    ├─► Vehicle Repair
    │   • Repair shop selected
    │   • Work order created
    │   • Repair timeline set
    │   • Progress monitored
    │   • Quality inspection
    │
    ├─► Vehicle Recovery
    │   • Repairs completed
    │   • Final inspection
    │   • Insurance claim settled
    │   • Vehicle returned to service
    │
    ↓

[RESOLUTION]
    │
    ├─► Case Resolution (Resolved)
    │   • Investigation findings documented
    │   • Financial impact calculated:
    │     - Repair costs
    │     - Insurance recovery
    │     - Excess paid
    │     - Net loss to organization
    │   • Lessons learned identified
    │   • Preventive actions implemented
    │
    ├─► Driver Action (if at fault)
    │   • Disciplinary hearing (if required)
    │   • Retraining recommended
    │   • Driving record updated
    │   • Performance review
    │
    ├─► Case Closed
    │   • Final report approved
    │   • Documentation archived
    │   • Stakeholders notified
    │   • Statistics updated
    │
    └─► Continuous Improvement
        • Review safety protocols
        • Update driver training
        • Enhance vehicle safety features
        • Implement preventive measures
```

### 5. Lost & Theft Incident Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                LOST & THEFT INCIDENT WORKFLOW                    │
│         (Based on Checklist_for_lost_and_theft_Form.pdf)        │
└─────────────────────────────────────────────────────────────────┘

[INCIDENT OCCURRENCE]
    │
    ├─► Incident Discovered
    │   • Theft, Loss, Hijacking, Burglary, or Vandalism
    │   • Immediate supervisor notified
    │   • Area secured if possible
    │   • Tracking company contacted (if equipped)
    │
    ↓

[IMMEDIATE RESPONSE]
    │
    ├─► Report Created (Draft)
    │   • Reporter details captured
    │   • Vehicle information recorded
    │   • Incident type classified:
    │     - Theft
    │     - Loss
    │     - Hijacking
    │     - Burglary
    │     - Vandalism
    │   • Date/time of incident
    │   • Discovery date/time
    │   • Location details (GPS if available)
    │   • Last known location
    │
    ├─► Detailed Documentation
    │   • Comprehensive incident description
    │   • Circumstances leading to incident
    │   • Last person with vehicle
    │   • Keys status and location
    │   • Documents status (registration, license disc)
    │   • Witnesses identified
    │   • Photos/evidence collected
    │   • Driver statement (if applicable)
    │
    ├─► Security Information
    │   • Alarm status (armed/disarmed)
    │   • Tracking device status (active/inactive)
    │   • Keys accountability (all keys accounted for?)
    │   • Spare keys location
    │   • Vehicle documents location
    │   • Last odometer reading
    │
    ├─► Submit Report (Reported)
    │   • Fleet manager auto-notified
    │   • Senior management alerted
    │   • Security department notified
    │   • Report locked for integrity
    │   • Report number generated (LT#####)
    │
    ↓

[INVESTIGATION PHASE]
    │
    ├─► Investigation Assigned (Under Investigation)
    │   • Investigation officer appointed
    │   • Initial assessment conducted
    │   • Evidence gathered
    │   • CCTV footage reviewed
    │   • Interviews conducted
    │   • Security logs checked
    │
    ├─► Security Measures Review
    │   • Alarm status checked
    │   • Tracking device status verified
    │   • Keys accountability confirmed
    │   • Documents location verified
    │   • Last known position tracked
    │   • Access control logs reviewed
    │
    ↓

[OFFICIAL REPORTING]
    │
    ├─► Police Report (Police Reported)
    │   • Case opened at police station
    │   • Case/docket number obtained
    │   • Investigating officer assigned
    │   • Statement provided
    │   • Police report copy attached
    │   • Vehicle marked as stolen in system
    │   • Vehicle details circulated
    │
    ├─► Tracking Company Notified
    │   • If tracking device fitted
    │   • Real-time tracking activated
    │   • Recovery attempts initiated
    │   • Location updates monitored
    │   • Police coordinated with
    │
    ↓

[INSURANCE CLAIM]
    │
    ├─► Insurance Notification (Insurance Claimed)
    │   • Insurance company contacted
    │   • Claim number obtained
    │   • Required documents submitted:
    │     - Police report
    │     - Vehicle registration
    │     - Keys status declaration
    │     - Maintenance records
    │     - Last service records
    │     - Proof of ownership
    │   • Insurance assessor assigned
    │
    ├─► Claim Processing
    │   • Assessor inspection (if vehicle recovered)
    │   • Valuation conducted
    │   • Claim status tracked
    │   • Settlement negotiation
    │
    ↓

[RECOVERY SCENARIOS]
    │
    ├─► VEHICLE RECOVERED
    │   • Recovery date recorded
    │   • Recovery location noted
    │   • Condition assessment
    │   • Damage documentation
    │   • Forensic examination
    │   • Missing items listed
    │   • Repair estimates obtained
    │   • Insurance claim adjusted
    │   • Decision: Repair or Write-off
    │   • Vehicle returned to service or scrapped
    │
    └─► VEHICLE NOT RECOVERED
        • Write-off processed
        • Insurance payout claimed
        • Asset register updated
        • Replacement vehicle requisitioned
        • Final settlement received

[RESOLUTION]
    │
    ├─► Case Resolution (Resolved)
    │   • Investigation findings documented
    │   • Financial impact calculated:
    │     - Total loss value
    │     - Insurance recovery
    │     - Excess paid
    │     - Net loss to organization
    │   • Lessons learned identified
    │   • Preventive actions implemented
    │
    ├─► Preventive Measures
    │   • Security upgrades implemented
    │   • Policy revisions made
    │   • Staff training conducted
    │   • Tracking improvements
    │   • Parking security enhanced
    │   • Access control strengthened
    │
    ├─► Case Closed
    │   • Final report approved
    │   • Documentation archived
    │   • Stakeholders notified
    │   • Statistics updated
    │   • Asset register updated
    │
    └─► Continuous Improvement
        • Review security protocols
        • Update risk assessments
        • Enhance monitoring systems
        • Staff awareness campaigns
        • Insurance policy review
```

### 6. Vehicle Relief/Replacement Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              VEHICLE RELIEF/REPLACEMENT WORKFLOW                 │
│            (Based on GFMS_Vehicle_relief_form.pdf)               │
└─────────────────────────────────────────────────────────────────┘

[RELIEF REQUEST]
    │
    ├─► Relief Needed
    │   • Original vehicle unavailable (maintenance, accident, etc.)
    │   • Temporary replacement required
    │   • Duration estimated
    │
    ├─► Relief Form Created
    │   • Original vehicle details
    │   • Reason for relief
    │   • Expected duration
    │   • Department/user information
    │   • Urgency level
    │
    ↓

[VEHICLE ASSIGNMENT]
    │
    ├─► Fleet Manager Reviews
    │   • Checks available vehicles
    │   • Matches category requirements
    │   • Verifies vehicle condition
    │   • Assigns replacement vehicle
    │
    ├─► Replacement Vehicle Assigned
    │   • Replacement vehicle details recorded
    │   • Driver notified
    │   • Handover arranged
    │   • Relief period documented
    │
    ↓

[VEHICLE HANDOVER]
    │
    ├─► Pre-Handover Checklist
    │   • Replacement vehicle inspected
    │   • Fuel level recorded
    │   • Odometer reading noted
    │   • Condition documented
    │   • Keys handed over
    │
    ├─► Relief Period
    │   • Replacement vehicle in use
    │   • Original vehicle being serviced/repaired
    │   • Relief period monitored
    │
    ↓

[VEHICLE RETURN]
    │
    ├─► Original Vehicle Ready
    │   • Repairs/maintenance completed
    │   • Vehicle inspected
    │   • Ready for return to service
    │
    ├─► Replacement Vehicle Returned
    │   • Post-use inspection
    │   • Fuel level checked
    │   • Odometer reading recorded
    │   • Any damage reported
    │   • Keys returned
    │
    ├─► Original Vehicle Returned
    │   • Vehicle handed back to user
    │   • Condition verified
    │   • Relief period closed
    │   • Documentation completed
    │
    └─► Relief Form Closed
        • All details finalized
        • Costs allocated
        • Records updated
```

### 7. Maintenance & Service Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              MAINTENANCE & SERVICE WORKFLOW                      │
│    (Based on TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf)      │
└─────────────────────────────────────────────────────────────────┘

[MAINTENANCE TRIGGER]
    │
    ├─► Scheduled Maintenance Due
    │   • Based on odometer reading
    │   • Based on time interval
    │   • Based on maintenance contract (FML/MM)
    │
    ├─► Unscheduled Maintenance
    │   • Vehicle checklist issues
    │   • Driver reported problems
    │   • Breakdown
    │
    ↓

[WORK ORDER CREATION]
    │
    ├─► Work Order Generated
    │   • Work order number (WO format)
    │   • Vehicle details
    │   • Service type
    │   • Service provider assigned
    │   • Expected completion date
    │   • Cost estimate
    │
    ├─► Service Provider Selection
    │   • Based on service type
    │   • Based on contract (FML providers)
    │   • Based on location
    │   • Based on availability
    │
    ↓

[SERVICE EXECUTION]
    │
    ├─► Vehicle Delivered
    │   • Vehicle dropped off
    │   • Odometer reading recorded
    │   • Issues documented
    │   • Expected pickup date set
    │
    ├─► Service Performed
    │   • Diagnostic checks
    │   • Repairs/maintenance done
    │   • Parts replaced (documented)
    │   • Quality checks
    │   • Test drive
    │
    ├─► Service Completed
    │   • Work completed
    │   • Invoice generated
    │   • Service report provided
    │   • Vehicle ready for collection
    │
    ↓

[VEHICLE COLLECTION]
    │
    ├─► Post-Service Inspection
    │   • Work verified
    │   • Vehicle condition checked
    │   • Test drive performed
    │   • Documentation reviewed
    │
    ├─► Payment Processing
    │   • Invoice verified
    │   • Cost approved
    │   • Payment authorized
    │   • Payment processed
    │
    ├─► Work Order Closed
    │   • Service history updated
    │   • Odometer reading updated
    │   • Next service scheduled
    │   • Documentation archived
    │
    └─► Vehicle Returned to Service
        • Vehicle status updated
        • Availability restored
        • Driver notified
```

## Key Features

### 1. **Automated Workflow Management**
- Status-driven workflows with validation
- Automatic notifications at each stage
- Role-based approvals
- Document generation automation
- Sequential trip numbering (matching Manual Trip Authorization format)
- Odometer tracking and history

### 2. **Comprehensive Data Capture**
- All fields from PDF forms digitized
- Vehicle categories aligned with Fleet Register
- Maintenance contract tracking (FML, MM)
- Cost center allocation
- Relational data linking
- Audit trail maintenance
- Document attachments support

### 3. **Security & Access Control**
- Role-based access (User, Manager, Administrator)
- Record-level security rules
- Department-based visibility
- Audit logging
- Data integrity protection

### 4. **Reporting & Analytics**
- QWeb PDF reports matching original forms
- Fleet utilization reports
- Maintenance cost analysis
- Incident statistics
- Trip frequency analysis
- Fuel consumption tracking
- Customizable report filters
- Export capabilities
- Dashboard widgets

### 5. **Integration**
- Seamless integration with HR module
- Fleet management extension
- Mail system integration
- Activity tracking
- Service provider management
- Cost tracking and allocation

### 6. **Compliance & Regulatory**
- RT46 form compliance
- Police reporting integration
- Insurance claim tracking
- License disc renewal monitoring
- Safety equipment verification
- Maintenance record keeping

## User Roles & Permissions

### Fleet User
- Create and view own transport requests
- View assigned trip authorities
- Complete vehicle checklists
- Report incidents
- View vehicle information
- **Cannot:** Delete records, approve requests, assign vehicles

### Fleet Manager
- All Fleet User permissions
- Approve transport requests
- Assign vehicles and drivers
- Issue trip authorities
- Review all checklists
- Investigate incidents
- Generate reports
- Manage maintenance schedules
- Approve service work orders
- **Cannot:** Delete certain system records, modify closed records

### Fleet Administrator
- All Fleet Manager permissions
- Full system configuration
- Security settings management
- Master data maintenance
- System-wide deletions
- Custom report creation
- User access management
- Vehicle category configuration
- Maintenance contract setup

## Technical Implementation

### Models Created
1. **fleet.transport.request** - Transport request management
2. **fleet.trip.authority** - Trip authorization and tracking
3. **fleet.vehicle.checklist** - Vehicle inspection checklists
4. **fleet.lost.theft** - Incident reporting and tracking (theft, loss, hijacking)
5. **fleet.accident.report** - Accident reporting and management
6. **fleet.vehicle.relief** - Vehicle relief/replacement tracking

### Model Extensions
- **fleet.vehicle** - Enhanced with:
  - Vehicle categories (1, 5, 6, 11, 15, MM)
  - Maintenance contract type (FML, MM)
  - Contract term and monthly cost
  - Accessories tracking
  - License renewal dates
  - Odometer history
  - Cost center allocation

- **res.partner** - Driver-specific fields added
- **fleet.vehicle.log.services** - Enhanced with work order tracking

### Reports Generated
1. Transport Request Form (PDF) - Based on Transport_request_form.pdf
2. Trip Authority Form (PDF) - Based on Trip_authority_Form.pdf
3. Vehicle Checklist Form (PDF) - Based on Vehicle_checklist_form.pdf
4. Lost & Theft Report (PDF) - Based on Checklist_for_lost_and_theft_Form.pdf
5. Accident Report (PDF) - Based on Checklist_for_accidents.pdf and RT46_accident_form.pdf
6. Vehicle Relief Form (PDF) - Based on GFMS_Vehicle_relief_form.pdf
7. Trip Register Report - Based on MANUAL_TRIP_AUTHORISATION_2018.pdf
8. Fleet Register Report - Based on FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf
9. Service History Report - Based on TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf

## Installation & Configuration

### Prerequisites
- Odoo 18.0
- Python 3.10+
- Required modules: base, fleet, hr, mail, web

### Installation Steps
1. Copy module to Odoo addons directory
2. Update apps list
3. Install "Enhanced Fleet Management"
4. Configure user groups
5. Set up sequences
6. Configure email templates
7. Import vehicle categories
8. Set up maintenance contracts

### Initial Configuration

1. **User Setup:**
   - Assign users to appropriate groups
   - Configure department managers
   - Set up fleet managers
   - Assign fleet administrators

2. **Master Data:**
   - Register all vehicles (from Fleet Register)
   - Configure vehicle categories
   - Add driver information
   - Set up departments
   - Configure service providers
   - Set up maintenance contracts
   - Configure email notifications

3. **Sequences:**
   - Transport Request: TR#####
   - Trip Authority: Sequential (GGG145776/01/2024 format)
   - Vehicle Checklist: VC#####
   - Lost/Theft: LT#####
   - Accident Report: AR#####
   - Work Order: WO#####

4. **Vehicle Categories Setup:**
   - Category 1: Sedans
   - Category 5: LDV 4x2 1 ton
   - Category 6: LDV 4x2 D/Cab
   - Category 11: LDV 4x4 1 ton light
   - Category 15: 16 Seater
   - MM: Ministerial vehicles

5. **Maintenance Contracts:**
   - FML: 60 months, cost range R6,684.82 - R13,459.09
   - MM: 120,000 KM, cost R1,232.45

## Best Practices

### For Employees
- Submit requests at least 48 hours in advance
- Provide complete and accurate information
- Mark urgent requests appropriately
- Update passenger information if changed
- Report incidents immediately

### For Managers
- Review requests promptly (within 24 hours)
- Verify business justification
- Consider cost implications
- Provide clear comments if rejected
- Monitor department vehicle usage

### For Fleet Managers
- Match vehicle to trip requirements by category
- Ensure driver availability and qualification
- Check vehicle maintenance status before assignment
- Issue authorities promptly
- Monitor overdue trips
- Track vehicle utilization
- Manage maintenance schedules
- Review incident reports

### For Drivers
- Complete pre-trip checklist thoroughly
- Report defects immediately
- Maintain fuel receipts
- Record accurate odometer readings
- Submit trip reports on time
- Report incidents immediately
- Follow safety protocols

### For Inspectors
- Be thorough and objective
- Document all issues clearly
- Take photos of damage
- Recommend preventive actions
- Never clear unsafe vehicles
- Follow checklist systematically
- Verify all safety equipment

### For Service Providers
- Provide accurate cost estimates
- Complete work within agreed timeframe
- Document all work performed
- Provide detailed invoices
- Maintain quality standards
- Report additional issues found

## Data Migration from PDF Documents

### Fleet Register Import
- Import vehicle data from FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf
- Preserve historical information
- Maintain vehicle categories
- Import maintenance contract details
- Set up cost centers

### Trip History Import
- Import trip data from MANUAL_TRIP_AUTHORISATION_2018.pdf
- Preserve odometer readings
- Maintain trip numbering sequence
- Import historical mileage data

### Service History Import
- Import service records from TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf
- Preserve work order numbers
- Import service provider details
- Maintain cost history

### Odometer History Import
- Import odometer data from Human_Settlements_Odo_metres.pdf
- Preserve vehicle replacement history
- Maintain usage tracking data

## Troubleshooting

### Common Issues
1. **Cannot submit request:** Check all required fields are filled
2. **Vehicle not appearing:** Verify vehicle is active and in correct category
3. **No approval notifications:** Check email configuration and user settings
4. **Report not printing:** Verify report templates installed correctly
5. **Access denied:** Check user group assignment and permissions
6. **Trip number not generating:** Check sequence configuration
7. **Odometer validation error:** Verify reading is higher than previous
8. **Maintenance contract not found:** Check vehicle category and contract setup

## Support & Maintenance

### Regular Maintenance Tasks
- **Daily:** Monitor pending requests and active trips
- **Weekly:** Review pending requests and overdue trips, check vehicle availability
- **Monthly:** Analyze fleet utilization reports, review maintenance schedules
- **Quarterly:** Review incident statistics, analyze costs, update service providers
- **Annually:** Update security protocols and forms, review contracts, plan replacements

### System Health Checks
- Monitor checklist completion rates
- Track average approval times
- Review incident trends
- Analyze vehicle condition scores
- Monitor maintenance costs
- Track fuel consumption
- Review trip frequency
- Analyze vehicle utilization

## Compliance & Audit

### Record Retention
- Transport Requests: 3 years
- Trip Authorities: 3 years
- Vehicle Checklists: 5 years
- Lost/Theft Reports: 7 years
- Accident Reports: 7 years
- Maintenance Records: Vehicle lifetime
- Service Invoices: 7 years

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
9. Automated license renewal reminders
10. Fleet optimization analytics
11. Carbon footprint tracking
12. Route optimization
13. Driver behavior monitoring
14. Automated fuel consumption analysis

---

## Document References

This process flow documentation is based on the following official PDF documents:

1. **Checklist_for_accidents.pdf** - Accident reporting checklist
2. **Checklist_for_lost_and_theft_Form.pdf** - Lost and theft incident form
3. **FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf** - Complete vehicle register
4. **GFMS_Vehicle_relief_form.pdf** - Vehicle relief/replacement form
5. **Human_Settlements_Odo_metres.pdf** - Odometer tracking records
6. **MANUAL_TRIP_AUTHORISATION_2018.pdf** - Trip authorization register
7. **RT46_accident_form.pdf** - Official accident report form
8. **TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf** - Service and maintenance records
9. **Transport_request_form.pdf** - Transport request template
10. **Trip_authority_Form.pdf** - Trip authority template
11. **Vehicle_checklist_form.pdf** - Vehicle inspection checklist

For detailed analysis of these documents, refer to **PDF_ANALYSIS_SUMMARY.md**

---

**Document Version:** 2.0.0
**Last Updated:** January 2026
**Module Version:** 18.0.1.0.0
**Author:** ECDHS
**Organization:** Department of Human Settlements
