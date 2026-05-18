# Enhanced Fleet Management Module - Quick Start Guide

**Version:** 18.0.2.0.0
**Forms Implemented:** 7 Core Forms
**Status:** Production Ready

## ⚠️ IMPORTANT: Troubleshooting

If you see errors related to `documents.folder` or `documents_fleet_folder`:
- **See [DOCUMENTS_REQUIREMENT.md](DOCUMENTS_REQUIREMENT.md)** for detailed fix
- **Quick Fix**: Install the "Documents" module from Odoo Apps
- **Alternative**: Uninstall "Documents - Fleet" module if you don't need it

## Installation Checklist

- [ ] **Check for documents_fleet module** (see warning above)
- [ ] Copy module to Odoo addons directory
- [ ] Update apps list in Odoo
- [ ] Install "Enhanced Fleet Management" module
- [ ] Configure user groups
- [ ] Assign users to appropriate roles
- [ ] Test email configuration
- [ ] Verify report printing (wkhtmltopdf)

## Quick Reference

### Creating a Transport Request
1. Fleet → Fleet Operations → Transport Requests
2. Click Create
3. Fill required fields (date, destination, purpose)
4. Click Submit

### Reporting an Accident (RT46)
1. Fleet → Fleet Operations → Accident Reports (RT46)
2. Click Create
3. Fill accident details, vehicle, driver
4. Add photos and witness information
5. Click Report Accident

### Requesting Vehicle Relief
1. Fleet → Fleet Operations → Vehicle Relief
2. Click Create
3. Select original vehicle and relief reason
4. Specify relief period
5. Click Submit

### Recording Odometer Reading
1. Fleet → Fleet Operations → Odometer Readings
2. Click Create
3. Select vehicle and enter reading
4. Add fuel level and condition notes
5. System auto-validates against previous reading

### Completing a Vehicle Checklist
1. Fleet → Fleet Operations → Vehicle Checklists
2. Click Create
3. Select vehicle and inspection type
4. Complete all sections (50+ checkpoints)
5. Mark roadworthy status
6. Click Complete Inspection

### Reporting an Incident
1. Fleet → Fleet Operations → Lost & Theft Reports
2. Click Create
3. Select incident type
4. Provide comprehensive details
5. Click Report Incident

## Module Structure

```
enhanced_fleet_management/
├── __init__.py
├── __manifest__.py
├── README.md
├── PROCESS_FLOW.md
├── QUICKSTART.md
├── IMPLEMENTATION_SUMMARY.md
├── data/
│   ├── sequence_data.xml (7 sequences)
│   └── mail_template_data.xml (4 templates)
├── models/
│   ├── __init__.py
│   ├── fleet_transport_request.py
│   ├── fleet_trip_authority.py
│   ├── fleet_vehicle_checklist.py
│   ├── fleet_lost_theft.py
│   ├── fleet_accident_report.py
│   ├── fleet_vehicle_relief.py
│   ├── fleet_odometer_reading.py
│   └── fleet_vehicle.py
├── views/
│   ├── fleet_transport_request_views.xml
│   ├── fleet_trip_authority_views.xml
│   ├── fleet_vehicle_checklist_views.xml
│   ├── fleet_lost_theft_views.xml
│   ├── fleet_accident_report_views.xml
│   ├── fleet_vehicle_relief_views.xml
│   ├── fleet_odometer_reading_views.xml
│   ├── fleet_vehicle_views.xml
│   └── fleet_menu_views.xml
├── report/
│   ├── __init__.py
│   ├── fleet_reports.xml
│   ├── transport_request_report_template.xml
│   ├── trip_authority_report_template.xml
│   ├── vehicle_checklist_report_template.xml
│   ├── lost_theft_report_template.xml
│   ├── accident_report_template.xml
│   ├── vehicle_relief_report_template.xml
│   └── odometer_reading_report_template.xml
├── security/
│   ├── fleet_security.xml (14 record rules)
│   └── ir.model.access.csv (21 access lines)
├── wizard/
│   ├── __init__.py
│   ├── fleet_report_wizard.py
│   └── fleet_report_wizard_views.xml
└── static/
    ├── description/
    │   └── icon.png
    └── src/
        ├── css/
        │   └── fleet_management.css
        ├── js/
        │   └── fleet_dashboard.js
        └── xml/
            └── fleet_dashboard.xml
```

## Key Workflows Summary

### Transport Request → Trip Authority → Completion
1. Employee creates transport request
2. Department Manager approves
3. Fleet Manager assigns vehicle & approves
4. System auto-creates Trip Authority
5. Pre-trip checklist completed
6. Trip executed
7. Post-trip checklist completed
8. Trip authority marked complete

### Accident Reporting Workflow
1. Driver/Employee reports accident
2. Photos and witness details captured
3. Police notification (if required)
4. Investigation initiated
5. Fault determination
6. Insurance claim filed
7. Claim processed
8. Report closed

### Vehicle Relief Workflow
1. Request relief vehicle (maintenance/accident)
2. Manager approval
3. Relief vehicle assigned
4. Handover checklist
5. Relief period active
6. Original vehicle ready
7. Return checklist
8. Relief closed

### Odometer Reading Validation
1. Enter reading (routine/trip/fuel)
2. System checks previous reading
3. Distance calculation
4. Suspicious reading detection
5. Manager verification (if needed)
6. Reading confirmed

### Vehicle Inspection Cycle
Pre-Trip → Journey → Post-Trip → Issues (if any) → Maintenance → Re-inspection

### Incident Management
Report → Investigation → Police Report → Insurance Claim → Resolution

## Important Notes

⚠️ **Security:** Always report incidents and accidents immediately
⚠️ **Checklists:** Never skip pre-trip inspections
⚠️ **Documentation:** Keep all receipts and documents
⚠️ **Compliance:** Follow all approval workflows
⚠️ **Odometer:** Report suspicious readings to manager
⚠️ **Relief Vehicles:** Complete handover checklists thoroughly

## Forms Reference

| Form | Menu Path | Use When |
|------|-----------|----------|
| Transport Request | Fleet Operations → Transport Requests | Need vehicle for official trip |
| Trip Authority | Fleet Operations → Trip Authorities | Automatically created from request |
| Vehicle Checklist | Fleet Operations → Vehicle Checklists | Pre/post trip or scheduled inspection |
| Lost & Theft | Fleet Operations → Lost & Theft Reports | Vehicle stolen or lost items |
| Accident Report (RT46) | Fleet Operations → Accident Reports | Vehicle involved in accident |
| Vehicle Relief | Fleet Operations → Vehicle Relief | Vehicle needs replacement |
| Odometer Reading | Fleet Operations → Odometer Readings | Regular tracking or trip recording |

## Support Contacts

- **Technical Issues:** System Administrator
- **Approval Queries:** Fleet Manager
- **Training:** HR Department
- **Accidents/Incidents:** Security/Fleet Manager (immediate)
- **Insurance Claims:** Finance/Fleet Manager

## Version Information

- **Module Version:** 18.0.2.0.0
- **Odoo Version:** 18.0
- **Release Date:** January 22, 2026
- **Author:** ECDHS
- **Forms Implemented:** 7 (Phase 1 Complete)
- **Forms Pending:** 4 (Phase 2)

---

For detailed documentation, see [README.md](README.md), [PROCESS_FLOW.md](PROCESS_FLOW.md), and [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
