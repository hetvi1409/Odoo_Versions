# Enhanced Fleet Management Module for Odoo 18

**Version:** 18.0.2.0.0
**Author:** ECDHS
**License:** LGPL-3
**Organization:** Department of Human Settlements

## Overview

The Enhanced Fleet Management module extends Odoo 18's standard fleet functionality with comprehensive forms and workflows based on Department of Human Settlements fleet management requirements. It digitizes and automates transport requests, trip authorities, vehicle inspections, accident reporting, vehicle relief management, and odometer tracking.

This module is specifically designed to replace and digitize all paper-based fleet management forms including:
- Transport Request Forms
- Trip Authority Forms
- Vehicle Checklist Forms
- Accident Report Forms (RT46)
- Lost & Theft Report Forms
- Vehicle Relief Forms (GFMS)
- Manual Trip Authorization Registers
- Fleet Register Management
- Service and Maintenance Tracking

## Key Highlights

✅ **100% PDF Form Compliance** - All 11 official PDF forms digitized and integrated
✅ **Vehicle Categories** - Full support for Categories 1, 5, 6, 11, 15, and MM vehicles
✅ **Maintenance Contracts** - FML (60 months) and MM (120,000 KM) contract tracking
✅ **Sequential Trip Numbering** - Matches Manual Trip Authorization format (GGG145776/01/2024)
✅ **Odometer History** - Complete tracking aligned with Human_Settlements_Odo_metres.pdf
✅ **Service Provider Management** - Work order tracking from Transit Solution records
✅ **RT46 Compliance** - Official accident reporting forms
✅ **Multi-level Approvals** - Department Manager → Fleet Manager workflow
✅ **Automated Notifications** - Email alerts at every workflow stage
✅ **Comprehensive Reporting** - PDF reports matching original forms

## Features

### 📋 Transport Request Management
- Complete digital transport request forms (based on Transport_request_form.pdf)
- Multi-level approval workflow (Department Manager → Fleet Manager)
- Vehicle and driver assignment by category
- Priority and urgency flags
- Email notifications at each stage
- PDF report generation matching original form
- Department and cost center tracking
- Passenger information management
- Special requirements capture

### 🚗 Trip Authority System
- Automated trip authority generation from approved requests (based on Trip_authority_Form.pdf)
- Sequential trip numbering (format: GGG145776/01/2024) matching MANUAL_TRIP_AUTHORISATION_2018.pdf
- Comprehensive trip details (schedule, route, passengers)
- Odometer and fuel tracking (start and end readings)
- Pre-trip and post-trip checklist integration
- Trip completion reports
- Authorization signatures
- Distance calculation (automatic)
- Fuel consumption tracking
- Trip history preservation

### ✅ Vehicle Inspection Checklists
- Comprehensive vehicle inspection forms (based on Vehicle_checklist_form.pdf)
- Pre-trip and post-trip inspections
- Scheduled maintenance checks
- Random inspection support
- Detailed component checking:
  - **Exterior:** Body, lights, mirrors, tyres, license disc
  - **Under hood:** Fluids (oil, coolant, brake, power steering, washer), battery, leaks
  - **Interior:** Seats, seatbelts, instruments, controls, air conditioning
  - **Safety equipment:** Fire extinguisher, first aid kit, warning triangle, jack, reflective vest
  - **Documents:** License disc, registration, insurance, service book
- Automatic roadworthiness assessment
- Issue tracking and recommendations
- Photo attachments support
- Inspector signature and driver acknowledgment
- Maintenance work order creation

### 🚨 Lost & Theft Incident Reporting
- Comprehensive incident documentation (based on Checklist_for_lost_and_theft_Form.pdf)
- Multiple incident types:
  - Theft
  - Loss
  - Hijacking
  - Burglary
  - Vandalism
- Police report tracking (case/docket number)
- Insurance claim management (claim number)
- Investigation workflow
- Recovery tracking (date, location, condition)
- Tracking device status monitoring
- Keys and documents accountability
- Financial impact calculation
- Preventive action planning
- Security measures review

### 🚑 Accident Reporting (RT46 Form)
- Official RT46 accident report forms (based on RT46_accident_form.pdf and Checklist_for_accidents.pdf)
- Detailed accident information capture
- Driver, passenger, and third-party details
- Weather and road conditions
- Police and emergency services integration
- Insurance claim management
- Fault determination
- Investigation tracking
- Severity level assessment (minor, moderate, major, fatal)
- Witness information
- Damage assessment
- Photo and document attachments
- Critical accident email alerts
- Repair cost tracking

### 🔄 Vehicle Relief Management (GFMS)
- Vehicle relief/replacement request workflow (based on GFMS_Vehicle_relief_form.pdf)
- Relief reason tracking:
  - Maintenance
  - Repair
  - Accident
  - Breakdown
  - Other
- Original and relief vehicle tracking
- Handover and return checklists
- Cost tracking and calculation
- Driver assignment
- Overdue relief tracking
- Related accident and maintenance linking
- Relief period monitoring
- Vehicle availability management

### 📏 Odometer Reading Tracking
- Regular odometer reading entry (based on Human_Settlements_Odo_metres.pdf)
- Automatic distance calculation
- Previous reading tracking
- Suspicious reading detection
- Fuel level monitoring
- Vehicle condition tracking
- Reading verification workflow
- Photo evidence support
- Multiple reading types:
  - Routine
  - Departure
  - Arrival
  - Maintenance
  - Refueling
- Historical odometer data preservation
- Mileage analysis and reporting

### 🔧 Service & Maintenance Management
- Work order tracking (based on TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf)
- Service provider management
- Work order numbering (WO format)
- Service type classification
- Cost tracking and approval
- Service history preservation
- Scheduled maintenance alerts
- Completion date tracking
- Invoice management
- Parts and labor tracking
- Quality inspection
- Service report generation

### 🚙 Fleet Register Management
- Complete vehicle register (based on FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf)
- Vehicle categories:
  - **Category 1:** Sedans (VW Polo Vivo, Toyota Etios, Nissan Almera, Hyundai Grand i10)
  - **Category 5:** LDV 4x2 1 ton (Isuzu D-MAX, Toyota Hilux, Ford Ranger)
  - **Category 6:** LDV 4x2 D/Cab (Isuzu D-MAX)
  - **Category 11:** LDV 4x4 1 ton light (Toyota Hilux, Isuzu D-MAX)
  - **Category 15:** 16 Seater (VW Crafter)
  - **MM Vehicles:** Ministerial vehicles (Audi Q7, BMW X4)
- Maintenance contract tracking:
  - **FML (Full Maintenance Lease):** 60 months, R6,684.82 - R13,459.09/month
  - **MM (Ministerial Maintenance):** 120,000 KM, R1,232.45/month
- Vehicle information:
  - Registration number
  - Description (make/model)
  - Chassis number
  - Engine number
  - Date received
  - Section assignment
  - Driver assignment
  - Accessories (radio, aircon, canopy)
  - License renewal date
  - Cost center allocation
  - Location/department

## Installation

### Prerequisites
- Odoo 18.0 or higher
- Python 3.10+
- Dependencies: `base`, `fleet`, `hr`, `mail`, `web`

### Installation Steps

1. **Copy the module to your Odoo addons directory:**
   ```bash
   cp -r enhanced_fleet_management /path/to/odoo/addons/
   ```

2. **Update the addons list:**
   - Navigate to Apps menu
   - Click "Update Apps List"
   - Search for "Enhanced Fleet Management"

3. **Install the module:**
   - Click "Install" on the Enhanced Fleet Management module
   - Wait for installation to complete

4. **Configure initial settings:**
   - Set up user groups
   - Configure email templates
   - Verify sequences
   - Import vehicle categories
   - Set up maintenance contracts

## Configuration

### User Groups

The module creates three user groups:

1. **Fleet User** - Regular employees who can:
   - Create transport requests
   - View their own requests and trips
   - Complete vehicle checklists
   - Report incidents
   - Submit odometer readings

2. **Fleet Manager** - Managers who can:
   - All Fleet User permissions
   - Approve transport requests
   - Assign vehicles and drivers
   - Issue trip authorities
   - Review all records
   - Investigate incidents
   - Approve maintenance work orders
   - Manage vehicle relief requests

3. **Fleet Administrator** - System administrators who can:
   - All Fleet Manager permissions
   - Configure system settings
   - Manage master data
   - Delete records
   - Access all reports
   - Configure vehicle categories
   - Set up maintenance contracts
   - Manage service providers

### Assign Users to Groups

Navigate to: **Settings → Users & Companies → Users**
- Edit user
- Go to "Access Rights" tab
- Assign appropriate Fleet Management group

### Vehicle Categories Setup

Navigate to: **Fleet → Configuration → Vehicle Categories**
- Create categories matching Fleet Register:
  - Category 1: Sedans
  - Category 5: LDV 4x2 1 ton
  - Category 6: LDV 4x2 D/Cab
  - Category 11: LDV 4x4 1 ton light
  - Category 15: 16 Seater
  - MM: Ministerial vehicles

### Maintenance Contracts Setup

Navigate to: **Fleet → Configuration → Maintenance Contracts**
- Set up FML contracts (60 months)
- Set up MM contracts (120,000 KM)
- Configure monthly costs
- Assign to vehicles

## Usage Guide

### For Employees: Creating a Transport Request

1. Navigate to **Fleet → Fleet Operations → Transport Requests**
2. Click **Create**
3. Fill in the form:
   - Trip details (date, time, destination)
   - Purpose of trip
   - Number of passengers
   - Special requirements
   - Department and cost center
4. Click **Submit** to send for approval
5. Track status in the form
6. Receive email notifications at each stage

### For Managers: Approving Requests

1. Navigate to **Fleet → Fleet Operations → Transport Requests**
2. Filter by "Submitted" status
3. Open request to review
4. Verify business justification
5. Add comments if needed
6. Click **Approve** (or **Cancel** if rejected)
7. System automatically notifies Fleet Manager

### For Fleet Managers: Assigning Vehicles

1. Review approved requests
2. Click **Assign Vehicle & Approve**
3. Select appropriate vehicle by category
4. Verify vehicle maintenance status
5. Select qualified driver
6. Add any fleet manager comments
7. Click **Save**
8. System auto-generates Trip Authority with sequential trip number
9. Pre-trip checklist auto-created

### For Drivers/Inspectors: Vehicle Checklists

1. Navigate to **Fleet → Fleet Operations → Vehicle Checklists**
2. Click **Create** (or open auto-generated checklist)
3. Select inspection type (pre-trip, post-trip, scheduled, random)
4. Record odometer reading
5. Complete all checklist sections:
   - Mark each item as OK, Not OK, or N/A
   - Note any issues found
   - Check all safety equipment
   - Verify documents (license disc, insurance)
6. Provide recommendations
7. Mark vehicle roadworthiness
8. Click **Complete Inspection**
9. Add inspector signature
10. Driver acknowledgment
11. Print checklist

### For Reporting Accidents

1. Navigate to **Fleet → Fleet Operations → Accident Reports**
2. Click **Create**
3. Fill in accident details:
   - Date, time, location
   - Weather and road conditions
   - Driver and vehicle information
   - Third-party details
   - Witness information
4. Describe accident comprehensively
5. Assess damage and severity
6. Upload photos
7. Click **Report Accident**
8. Follow up with:
   - Police report (add case/docket number)
   - RT46 form completion
   - Insurance claim (add claim number)
   - Investigation findings
   - Repair estimates
   - Resolution details

### For Reporting Lost & Theft Incidents

1. Navigate to **Fleet → Fleet Operations → Lost & Theft Reports**
2. Click **Create**
3. Select incident type (theft, loss, hijacking, burglary, vandalism)
4. Fill in all incident details:
   - Incident date/time
   - Discovery date/time
   - Location
   - Last known position
   - Keys and documents status
   - Tracking device status
5. Describe incident comprehensively
6. Click **Report Incident**
7. Follow up with:
   - Police report (add case number)
   - Insurance claim (add claim number)
   - Investigation findings
   - Recovery details (if recovered)
   - Resolution and preventive actions

### For Vehicle Relief Requests

1. Navigate to **Fleet → Fleet Operations → Vehicle Relief**
2. Click **Create**
3. Select original vehicle
4. Select relief reason (maintenance, repair, accident, breakdown)
5. Specify expected duration
6. Click **Submit**
7. Fleet Manager assigns relief vehicle
8. Complete handover checklist
9. Monitor relief period
10. Complete return checklist when original vehicle ready

### For Odometer Readings

1. Navigate to **Fleet → Fleet Operations → Odometer Readings**
2. Click **Create**
3. Select vehicle
4. Select reading type (routine, departure, arrival, maintenance, refueling)
5. Enter odometer reading
6. Note fuel level
7. Record vehicle condition
8. Upload photo (optional)
9. Click **Submit**
10. System validates reading against previous
11. Distance automatically calculated

## Printing Reports

All forms can be printed as PDF reports matching original forms:

1. Open any record (Transport Request, Trip Authority, etc.)
2. Click **Print** button in the header
3. Select the appropriate report:
   - Transport Request Form
   - Trip Authority Form
   - Vehicle Checklist Form
   - Accident Report (RT46)
   - Lost & Theft Report
   - Vehicle Relief Form
   - Trip Register Report
   - Fleet Register Report
   - Service History Report
4. PDF will be generated and downloaded

Alternatively:
- Use the **Print Request/Authority/Checklist** button in the form

## Menu Structure

```
Fleet (Main Menu)
├── Fleet Operations
│   ├── Transport Requests
│   ├── Trip Authorities
│   ├── Vehicle Checklists
│   ├── Lost & Theft Reports
│   ├── Accident Reports (RT46)
│   ├── Vehicle Relief
│   └── Odometer Readings
├── Vehicles
│   ├── All Vehicles
│   ├── Vehicle Categories
│   └── Maintenance Contracts
├── Drivers
├── Service Providers
├── Reports
│   ├── Fleet Register Report
│   ├── Trip Register Report
│   ├── Service History Report
│   ├── Incident Statistics
│   ├── Maintenance Cost Analysis
│   └── Vehicle Utilization Report
└── Configuration
    ├── Settings
    ├── Vehicle Categories
    ├── Maintenance Contracts
    └── Service Providers
```

## Process Flows

See [PROCESS_FLOW.md](PROCESS_FLOW.md) for detailed workflow diagrams including:
- Transport Request approval workflow
- Trip Authority lifecycle with sequential numbering
- Vehicle inspection process
- Lost & Theft incident handling
- Accident reporting and investigation (RT46)
- Vehicle relief/replacement process
- Maintenance and service workflow
- Odometer tracking process

## PDF Documents Reference

This module digitizes and implements all requirements from the following official PDF documents:

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

## Technical Details

### Models

1. **fleet.transport.request** - Transport request management
2. **fleet.trip.authority** - Trip authorization and tracking
3. **fleet.vehicle.checklist** - Vehicle inspection checklists
4. **fleet.lost.theft** - Lost & theft incident reporting
5. **fleet.accident.report** - Accident reporting (RT46)
6. **fleet.vehicle.relief** - Vehicle relief/replacement
7. **fleet.odometer.reading** - Odometer tracking

### Model Extensions

- **fleet.vehicle** - Enhanced with categories, maintenance contracts, cost tracking
- **res.partner** - Driver-specific fields
- **fleet.vehicle.log.services** - Work order tracking

### Sequences

- Transport Request: `TR#####`
- Trip Authority: Sequential format `GGG145776/01/2024`
- Vehicle Checklist: `VC#####`
- Lost/Theft Report: `LT#####`
- Accident Report: `AR#####`
- Vehicle Relief: `VR#####`
- Odometer Reading: `OR#####`
- Work Order: `WO#####`

### Reports

1. Transport Request Form (PDF)
2. Trip Authority Form (PDF)
3. Vehicle Checklist Form (PDF)
4. Lost & Theft Report (PDF)
5. Accident Report (RT46) (PDF)
6. Vehicle Relief Form (PDF)
7. Trip Register Report (PDF)
8. Fleet Register Report (PDF)
9. Service History Report (PDF)

## Data Migration

The module supports importing historical data from PDF documents:

### Fleet Register Import
- Import vehicle data from FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf
- Preserve vehicle categories and maintenance contracts
- Import cost center allocations

### Trip History Import
- Import trip data from MANUAL_TRIP_AUTHORISATION_2018.pdf
- Preserve odometer readings and trip numbers
- Maintain sequential numbering

### Service History Import
- Import service records from TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf
- Preserve work order numbers and costs
- Import service provider details

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

### Support

For technical support or questions:
- Review documentation in [PROCESS_FLOW.md](PROCESS_FLOW.md)
- Check [PDF_ANALYSIS_SUMMARY.md](PDF_ANALYSIS_SUMMARY.md) for requirements
- Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
- Contact ECDHS support team

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

## Best Practices

### For Employees
- Submit requests at least 48 hours in advance
- Provide complete and accurate information
- Mark urgent requests appropriately
- Report incidents immediately

### For Managers
- Review requests promptly (within 24 hours)
- Verify business justification
- Consider cost implications
- Provide clear comments if rejected

### For Fleet Managers
- Match vehicle to trip requirements by category
- Ensure driver availability and qualification
- Check vehicle maintenance status before assignment
- Issue authorities promptly
- Monitor overdue trips
- Track vehicle utilization

### For Drivers
- Complete pre-trip checklist thoroughly
- Report defects immediately
- Maintain fuel receipts
- Record accurate odometer readings
- Submit trip reports on time
- Report incidents immediately

### For Inspectors
- Be thorough and objective
- Document all issues clearly
- Take photos of damage
- Recommend preventive actions
- Never clear unsafe vehicles

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

## License

This module is licensed under LGPL-3.

## Credits

**Author:** ECDHS
**Organization:** Department of Human Settlements
**Version:** 18.0.2.0.0
**Odoo Version:** 18.0

---

For detailed process flows and technical documentation, see:
- [PROCESS_FLOW.md](PROCESS_FLOW.md) - Comprehensive workflow documentation
- [PDF_ANALYSIS_SUMMARY.md](PDF_ANALYSIS_SUMMARY.md) - Analysis of all PDF requirements
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- [DOCUMENTS_REQUIREMENT.md](DOCUMENTS_REQUIREMENT.md) - Document requirements
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
