#!/usr/bin/env python3
"""
Generate Technical & Setup Guide for Enhanced Fleet Management Module
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from datetime import datetime

def add_heading(doc, text, level=1):
    """Add a formatted heading"""
    heading = doc.add_heading(text, level=level)
    return heading

def add_paragraph(doc, text, bold=False, italic=False):
    """Add a formatted paragraph"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    return p

def add_bullet_point(doc, text, level=0):
    """Add a bullet point"""
    p = doc.add_paragraph(text, style='List Bullet')
    if level > 0:
        p.paragraph_format.left_indent = Inches(0.5 * level)
    return p

def add_numbered_point(doc, text, level=0):
    """Add a numbered point"""
    p = doc.add_paragraph(text, style='List Number')
    if level > 0:
        p.paragraph_format.left_indent = Inches(0.5 * level)
    return p

def add_code_block(doc, code_text):
    """Add a code block"""
    p = doc.add_paragraph(code_text)
    p.style = 'No Spacing'
    run = p.runs[0]
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    p.paragraph_format.left_indent = Inches(0.5)
    return p

def create_technical_guide():
    """Create the Technical & Setup Guide document"""
    doc = Document()
    
    # Title Page
    title = doc.add_heading('Enhanced Fleet Management Module', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_heading('Technical & Setup Guide', level=1)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run('Version: 18.0.2.0.0\n').bold = True
    info.add_run('For Odoo 18.0\n')
    info.add_run('Department of Human Settlements\n')
    info.add_run(f'Generated: {datetime.now().strftime("%B %d, %Y")}\n')
    
    doc.add_page_break()
    
    # Table of Contents
    add_heading(doc, 'Table of Contents', 1)
    add_paragraph(doc, '1. Introduction')
    add_paragraph(doc, '2. System Requirements')
    add_paragraph(doc, '3. Installation Guide')
    add_paragraph(doc, '4. Module Architecture')
    add_paragraph(doc, '5. Database Schema')
    add_paragraph(doc, '6. Configuration Guide')
    add_paragraph(doc, '7. Security & Access Control')
    add_paragraph(doc, '8. Integration Points')
    add_paragraph(doc, '9. Customization Guide')
    add_paragraph(doc, '10. Troubleshooting')
    add_paragraph(doc, '11. API Reference')
    add_paragraph(doc, '12. Maintenance & Updates')
    
    doc.add_page_break()
    
    # 1. Introduction
    add_heading(doc, '1. Introduction', 1)
    
    add_heading(doc, '1.1 Overview', 2)
    add_paragraph(doc, 'The Enhanced Fleet Management module is a comprehensive solution designed specifically for the Department of Human Settlements to digitize and automate all fleet management operations. This module extends Odoo 18\'s standard fleet functionality with specialized forms, workflows, and reporting capabilities.')
    
    add_heading(doc, '1.2 Key Features', 2)
    add_bullet_point(doc, 'Complete digitization of 11 official PDF forms')
    add_bullet_point(doc, 'Multi-level approval workflows')
    add_bullet_point(doc, 'Sequential trip numbering (GGG145776/01/2024 format)')
    add_bullet_point(doc, 'Vehicle category management (Categories 1, 5, 6, 11, 15, MM)')
    add_bullet_point(doc, 'Maintenance contract tracking (FML 60 months, MM 120,000 KM)')
    add_bullet_point(doc, 'Comprehensive reporting and analytics')
    add_bullet_point(doc, 'Email notifications and alerts')
    add_bullet_point(doc, 'Mobile-responsive interface')
    
    add_heading(doc, '1.3 Module Components', 2)
    add_bullet_point(doc, 'Transport Request Management')
    add_bullet_point(doc, 'Trip Authority System')
    add_bullet_point(doc, 'Vehicle Inspection Checklists')
    add_bullet_point(doc, 'Accident Reporting (RT46)')
    add_bullet_point(doc, 'Lost & Theft Incident Reporting')
    add_bullet_point(doc, 'Vehicle Relief Management (GFMS)')
    add_bullet_point(doc, 'Odometer Reading Tracking')
    add_bullet_point(doc, 'Service & Maintenance Management')
    add_bullet_point(doc, 'Fleet Register Management')
    
    doc.add_page_break()
    
    # 2. System Requirements
    add_heading(doc, '2. System Requirements', 1)
    
    add_heading(doc, '2.1 Server Requirements', 2)
    add_paragraph(doc, 'Minimum Hardware:')
    add_bullet_point(doc, 'CPU: 4 cores (8 cores recommended)')
    add_bullet_point(doc, 'RAM: 8 GB (16 GB recommended)')
    add_bullet_point(doc, 'Storage: 50 GB SSD (100 GB recommended)')
    add_bullet_point(doc, 'Network: 100 Mbps (1 Gbps recommended)')
    
    add_paragraph(doc, '\nOperating System:')
    add_bullet_point(doc, 'Ubuntu 20.04 LTS or higher')
    add_bullet_point(doc, 'Debian 11 or higher')
    add_bullet_point(doc, 'CentOS 8 or higher')
    add_bullet_point(doc, 'Windows Server 2019 or higher (not recommended)')
    
    add_heading(doc, '2.2 Software Requirements', 2)
    add_bullet_point(doc, 'Odoo 18.0 or higher')
    add_bullet_point(doc, 'Python 3.10 or higher')
    add_bullet_point(doc, 'PostgreSQL 13 or higher')
    add_bullet_point(doc, 'wkhtmltopdf 0.12.6 (for PDF reports)')
    add_bullet_point(doc, 'Node.js 16+ (for asset compilation)')
    
    add_heading(doc, '2.3 Dependencies', 2)
    add_paragraph(doc, 'Required Odoo Modules:')
    add_bullet_point(doc, 'base - Core Odoo functionality')
    add_bullet_point(doc, 'fleet - Standard fleet management')
    add_bullet_point(doc, 'hr - Human resources integration')
    add_bullet_point(doc, 'mail - Email and messaging')
    add_bullet_point(doc, 'web - Web interface')
    
    add_paragraph(doc, '\nPython Libraries:')
    add_code_block(doc, 'lxml>=4.6.0\nPillow>=8.0.0\nreportlab>=3.5.0\npython-dateutil>=2.8.0')
    
    add_heading(doc, '2.4 Browser Requirements', 2)
    add_bullet_point(doc, 'Google Chrome 90+ (recommended)')
    add_bullet_point(doc, 'Mozilla Firefox 88+')
    add_bullet_point(doc, 'Microsoft Edge 90+')
    add_bullet_point(doc, 'Safari 14+ (macOS/iOS)')
    
    doc.add_page_break()
    
    # 3. Installation Guide
    add_heading(doc, '3. Installation Guide', 1)
    
    add_heading(doc, '3.1 Pre-Installation Checklist', 2)
    add_numbered_point(doc, 'Verify Odoo 18 is installed and running')
    add_numbered_point(doc, 'Ensure PostgreSQL database is accessible')
    add_numbered_point(doc, 'Confirm all dependencies are installed')
    add_numbered_point(doc, 'Backup existing database (if upgrading)')
    add_numbered_point(doc, 'Review system requirements')
    
    add_heading(doc, '3.2 Installation Steps', 2)
    
    add_paragraph(doc, 'Step 1: Download the Module', bold=True)
    add_code_block(doc, 'cd /path/to/odoo/addons\ngit clone <repository_url> enhanced_fleet_management')
    
    add_paragraph(doc, '\nStep 2: Set Permissions', bold=True)
    add_code_block(doc, 'sudo chown -R odoo:odoo enhanced_fleet_management\nsudo chmod -R 755 enhanced_fleet_management')
    
    add_paragraph(doc, '\nStep 3: Update Addons Path', bold=True)
    add_paragraph(doc, 'Edit your Odoo configuration file (odoo.conf):')
    add_code_block(doc, 'addons_path = /path/to/odoo/addons,/path/to/odoo/addons/enhanced_fleet_management')
    
    add_paragraph(doc, '\nStep 4: Restart Odoo Service', bold=True)
    add_code_block(doc, 'sudo systemctl restart odoo')
    
    add_paragraph(doc, '\nStep 5: Update Apps List', bold=True)
    add_numbered_point(doc, 'Log in to Odoo as Administrator')
    add_numbered_point(doc, 'Navigate to Apps menu')
    add_numbered_point(doc, 'Click "Update Apps List"')
    add_numbered_point(doc, 'Search for "Enhanced Fleet Management"')
    
    add_paragraph(doc, '\nStep 6: Install the Module', bold=True)
    add_numbered_point(doc, 'Click "Install" button')
    add_numbered_point(doc, 'Wait for installation to complete')
    add_numbered_point(doc, 'Verify no errors in log')
    
    add_heading(doc, '3.3 Post-Installation Verification', 2)
    add_numbered_point(doc, 'Check that all menus appear in Fleet menu')
    add_numbered_point(doc, 'Verify demo data loaded (if enabled)')
    add_numbered_point(doc, 'Test email template configuration')
    add_numbered_point(doc, 'Verify sequence generation')
    add_numbered_point(doc, 'Check user groups created')
    
    doc.add_page_break()
    
    # 4. Module Architecture
    add_heading(doc, '4. Module Architecture', 1)
    
    add_heading(doc, '4.1 Directory Structure', 2)
    add_code_block(doc, '''enhanced_fleet_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── fleet_vehicle.py
│   ├── fleet_transport_request.py
│   ├── fleet_trip_authority.py
│   ├── fleet_vehicle_checklist.py
│   ├── fleet_accident_report.py
│   ├── fleet_lost_theft.py
│   ├── fleet_vehicle_relief.py
│   └── fleet_odometer_reading.py
├── views/
│   ├── fleet_vehicle_views.xml
│   ├── fleet_transport_request_views.xml
│   ├── fleet_trip_authority_views.xml
│   ├── fleet_vehicle_checklist_views.xml
│   ├── fleet_accident_report_views.xml
│   ├── fleet_lost_theft_views.xml
│   ├── fleet_vehicle_relief_views.xml
│   ├── fleet_odometer_reading_views.xml
│   └── fleet_menu.xml
├── wizard/
│   ├── __init__.py
│   └── fleet_report_wizard.py
├── report/
│   ├── __init__.py
│   ├── fleet_reports.xml
│   └── report_templates.xml
├── security/
│   ├── ir.model.access.csv
│   └── fleet_security.xml
├── data/
│   ├── sequence_data.xml
│   ├── mail_template_data.xml
│   └── demo_data.xml
└── static/
    ├── description/
    │   ├── icon.png
    │   └── index.html
    └── src/
        ├── css/
        └── js/''')
    
    add_heading(doc, '4.2 Model Relationships', 2)
    add_paragraph(doc, 'Core Models and Their Relationships:')
    add_bullet_point(doc, 'fleet.vehicle (Extended) - Central vehicle registry')
    add_bullet_point(doc, 'fleet.transport.request - Transport booking requests')
    add_bullet_point(doc, 'fleet.trip.authority - Authorized trips (linked to requests)')
    add_bullet_point(doc, 'fleet.vehicle.checklist - Pre/post-trip inspections')
    add_bullet_point(doc, 'fleet.accident.report - Accident documentation')
    add_bullet_point(doc, 'fleet.lost.theft - Security incidents')
    add_bullet_point(doc, 'fleet.vehicle.relief - Vehicle replacements')
    add_bullet_point(doc, 'fleet.odometer.reading - Mileage tracking')
    
    add_heading(doc, '4.3 Workflow Engine', 2)
    add_paragraph(doc, 'The module uses Odoo\'s state machine pattern for workflow management:')
    add_bullet_point(doc, 'State transitions with validation')
    add_bullet_point(doc, 'Automated email notifications')
    add_bullet_point(doc, 'Activity scheduling')
    add_bullet_point(doc, 'Approval routing')
    add_bullet_point(doc, 'Audit trail logging')
    
    doc.add_page_break()
    
    # 5. Database Schema
    add_heading(doc, '5. Database Schema', 1)
    
    add_heading(doc, '5.1 Extended fleet.vehicle Fields', 2)
    add_paragraph(doc, 'New fields added to standard fleet.vehicle model:')
    add_code_block(doc, '''vehicle_category: Selection (cat1, cat5, cat6, cat11, cat15, mm, bus, motorcycle, trailer)
chassis_number: Char
engine_number: Char
date_received: Date
section_assignment: Char
cost_center: Char
maintenance_contract_type: Selection (fml, mm, none)
contract_term: Integer (months)
contract_km_coverage: Integer
monthly_cost: Float
has_radio: Boolean
has_aircon: Boolean
has_canopy: Boolean
license_renewal_date: Date
insurance_company: Char
insurance_policy_number: Char
insurance_expiry_date: Date
alarm_fitted: Boolean
tracking_device_fitted: Boolean
tracking_company: Char''')
    
    add_heading(doc, '5.2 fleet.transport.request Schema', 2)
    add_code_block(doc, '''name: Char (auto-generated TR#####)
requester_id: Many2one(res.partner)
department: Char
contact_number: Char
email: Char
request_date: Date
departure_date: Date
departure_time: Float
return_date: Date
return_time: Float
destination: Text
purpose: Text
number_of_passengers: Integer
passenger_names: Text
special_requirements: Text
urgency: Boolean
state: Selection (draft, submitted, dept_approved, approved, assigned, in_progress, completed, cancelled)
vehicle_id: Many2one(fleet.vehicle)
driver_id: Many2one(res.partner)
trip_authority_id: Many2one(fleet.trip.authority)''')
    
    add_heading(doc, '5.3 fleet.trip.authority Schema', 2)
    add_code_block(doc, '''trip_number: Char (auto-generated GGG145776/01/2024)
transport_request_id: Many2one(fleet.transport.request)
vehicle_id: Many2one(fleet.vehicle)
driver_id: Many2one(res.partner)
employee_id: Many2one(res.partner)
departure_date: Date
departure_time: Float
return_date: Date
return_time: Float
actual_return_date: Datetime
route_description: Text
purpose: Text
number_of_passengers: Integer
odometer_start: Float
fuel_level_start: Selection
odometer_end: Float
fuel_level_end: Selection
distance_travelled: Float (computed)
state: Selection (draft, issued, in_progress, completed, cancelled)''')
    
    add_heading(doc, '5.4 Indexes and Constraints', 2)
    add_paragraph(doc, 'Database indexes for performance:')
    add_bullet_point(doc, 'Index on trip_number (unique)')
    add_bullet_point(doc, 'Index on vehicle_id + departure_date')
    add_bullet_point(doc, 'Index on driver_id + state')
    add_bullet_point(doc, 'Index on request_date + state')
    
    doc.add_page_break()
    
    # 6. Configuration Guide
    add_heading(doc, '6. Configuration Guide', 1)
    
    add_heading(doc, '6.1 Initial Setup Wizard', 2)
    add_paragraph(doc, 'After installation, complete the setup wizard:')
    add_numbered_point(doc, 'Navigate to Fleet → Configuration → Settings')
    add_numbered_point(doc, 'Configure company information')
    add_numbered_point(doc, 'Set up email server (for notifications)')
    add_numbered_point(doc, 'Configure default values')
    add_numbered_point(doc, 'Import vehicle categories')
    add_numbered_point(doc, 'Set up maintenance contracts')
    
    add_heading(doc, '6.2 User Groups Configuration', 2)
    add_paragraph(doc, 'Three user groups are automatically created:')
    
    add_paragraph(doc, '\n1. Fleet User', bold=True)
    add_bullet_point(doc, 'Create transport requests')
    add_bullet_point(doc, 'View own requests and trips')
    add_bullet_point(doc, 'Complete vehicle checklists')
    add_bullet_point(doc, 'Report incidents')
    add_bullet_point(doc, 'Submit odometer readings')
    
    add_paragraph(doc, '\n2. Fleet Manager', bold=True)
    add_bullet_point(doc, 'All Fleet User permissions')
    add_bullet_point(doc, 'Approve transport requests')
    add_bullet_point(doc, 'Assign vehicles and drivers')
    add_bullet_point(doc, 'Issue trip authorities')
    add_bullet_point(doc, 'Review all records')
    add_bullet_point(doc, 'Investigate incidents')
    
    add_paragraph(doc, '\n3. Fleet Administrator', bold=True)
    add_bullet_point(doc, 'All Fleet Manager permissions')
    add_bullet_point(doc, 'Configure system settings')
    add_bullet_point(doc, 'Manage master data')
    add_bullet_point(doc, 'Delete records')
    add_bullet_point(doc, 'Access all reports')
    
    add_heading(doc, '6.3 Email Template Configuration', 2)
    add_paragraph(doc, 'Configure email templates for notifications:')
    add_numbered_point(doc, 'Navigate to Settings → Technical → Email → Templates')
    add_numbered_point(doc, 'Locate Enhanced Fleet Management templates')
    add_numbered_point(doc, 'Customize subject lines and content')
    add_numbered_point(doc, 'Test email delivery')
    
    add_heading(doc, '6.4 Sequence Configuration', 2)
    add_paragraph(doc, 'Verify and customize sequence numbering:')
    add_bullet_point(doc, 'Transport Request: TR##### (5 digits)')
    add_bullet_point(doc, 'Trip Authority: GGG145776/01/2024 (sequential)')
    add_bullet_point(doc, 'Accident Report: AR##### (5 digits)')
    add_bullet_point(doc, 'Lost/Theft: LT##### (5 digits)')
    add_bullet_point(doc, 'Vehicle Relief: VR##### (5 digits)')
    
    add_heading(doc, '6.5 Vehicle Categories Setup', 2)
    add_paragraph(doc, 'Configure vehicle categories based on fleet register:')
    add_code_block(doc, '''Category 1: Sedans (VW Polo Vivo, Toyota Etios, Nissan Almera, Hyundai Grand i10)
Category 5: LDV 4x2 1 ton (Isuzu D-MAX, Toyota Hilux, Ford Ranger)
Category 6: LDV 4x2 D/Cab (Isuzu D-MAX)
Category 11: LDV 4x4 1 ton light (Toyota Hilux, Isuzu D-MAX)
Category 15: 16 Seater (VW Crafter)
MM Vehicles: Ministerial vehicles (Audi Q7, BMW X4)
Bus: Passenger buses
Motorcycle: Motorcycles and scooters
Trailer: Utility trailers''')
    
    add_heading(doc, '6.6 Maintenance Contract Setup', 2)
    add_paragraph(doc, 'Configure maintenance contract types:')
    add_bullet_point(doc, 'FML (Full Maintenance Lease): 60 months, R6,684.82 - R13,459.09/month')
    add_bullet_point(doc, 'MM (Ministerial Maintenance): 120,000 KM, R1,232.45/month')
    add_bullet_point(doc, 'None: No maintenance contract')
    
    doc.add_page_break()
    
    # 7. Security & Access Control
    add_heading(doc, '7. Security & Access Control', 1)
    
    add_heading(doc, '7.1 Record Rules', 2)
    add_paragraph(doc, 'Record-level security rules:')
    add_bullet_point(doc, 'Users can only view their own requests (unless manager)')
    add_bullet_point(doc, 'Managers can view all records in their department')
    add_bullet_point(doc, 'Administrators have full access')
    add_bullet_point(doc, 'Drivers can view assigned trips')
    
    add_heading(doc, '7.2 Field-Level Security', 2)
    add_paragraph(doc, 'Sensitive fields are protected:')
    add_bullet_point(doc, 'Cost information (managers only)')
    add_bullet_point(doc, 'Insurance details (administrators only)')
    add_bullet_point(doc, 'Investigation notes (managers only)')
    add_bullet_point(doc, 'Approval signatures (system-generated)')
    
    add_heading(doc, '7.3 Audit Trail', 2)
    add_paragraph(doc, 'All changes are logged:')
    add_bullet_point(doc, 'User who made the change')
    add_bullet_point(doc, 'Timestamp of change')
    add_bullet_point(doc, 'Old and new values')
    add_bullet_point(doc, 'IP address (if available)')
    
    add_heading(doc, '7.4 Data Encryption', 2)
    add_paragraph(doc, 'Sensitive data encryption:')
    add_bullet_point(doc, 'Database encryption at rest')
    add_bullet_point(doc, 'SSL/TLS for data in transit')
    add_bullet_point(doc, 'Password hashing (bcrypt)')
    add_bullet_point(doc, 'API token encryption')
    
    doc.add_page_break()
    
    # 8. Integration Points
    add_heading(doc, '8. Integration Points', 1)
    
    add_heading(doc, '8.1 Standard Odoo Modules', 2)
    add_bullet_point(doc, 'Fleet: Vehicle and driver management')
    add_bullet_point(doc, 'HR: Employee information')
    add_bullet_point(doc, 'Mail: Email notifications and chatter')
    add_bullet_point(doc, 'Calendar: Trip scheduling')
    add_bullet_point(doc, 'Contacts: Driver and employee records')
    
    add_heading(doc, '8.2 External Systems', 2)
    add_paragraph(doc, 'Integration capabilities:')
    add_bullet_point(doc, 'GPS tracking systems (API integration)')
    add_bullet_point(doc, 'Fuel card systems (CSV import)')
    add_bullet_point(doc, 'Insurance portals (API integration)')
    add_bullet_point(doc, 'Maintenance providers (email/API)')
    add_bullet_point(doc, 'Financial systems (export to CSV/Excel)')
    
    add_heading(doc, '8.3 API Endpoints', 2)
    add_paragraph(doc, 'RESTful API endpoints available:')
    add_code_block(doc, '''GET /api/fleet/vehicles - List all vehicles
GET /api/fleet/vehicles/{id} - Get vehicle details
POST /api/fleet/transport-requests - Create transport request
GET /api/fleet/trip-authorities - List trip authorities
POST /api/fleet/odometer-readings - Submit odometer reading
GET /api/fleet/reports/summary - Get fleet summary report''')
    
    add_heading(doc, '8.4 Webhooks', 2)
    add_paragraph(doc, 'Webhook events for external systems:')
    add_bullet_point(doc, 'transport_request.created')
    add_bullet_point(doc, 'transport_request.approved')
    add_bullet_point(doc, 'trip_authority.issued')
    add_bullet_point(doc, 'accident.reported')
    add_bullet_point(doc, 'vehicle.maintenance_due')
    
    doc.add_page_break()
    
    # 9. Customization Guide
    add_heading(doc, '9. Customization Guide', 1)
    
    add_heading(doc, '9.1 Adding Custom Fields', 2)
    add_paragraph(doc, 'To add custom fields to models:')
    add_numbered_point(doc, 'Create a new module that depends on enhanced_fleet_management')
    add_numbered_point(doc, 'Inherit the target model')
    add_numbered_point(doc, 'Add your custom fields')
    add_numbered_point(doc, 'Update views to display new fields')
    
    add_paragraph(doc, '\nExample:')
    add_code_block(doc, '''from odoo import models, fields

class FleetVehicleCustom(models.Model):
    _inherit = 'fleet.vehicle'
    
    custom_field = fields.Char('Custom Field')
    custom_date = fields.Date('Custom Date')''')
    
    add_heading(doc, '9.2 Customizing Workflows', 2)
    add_paragraph(doc, 'To modify approval workflows:')
    add_numbered_point(doc, 'Inherit the model with workflow')
    add_numbered_point(doc, 'Override state transition methods')
    add_numbered_point(doc, 'Add custom validation logic')
    add_numbered_point(doc, 'Update email templates')
    
    add_heading(doc, '9.3 Custom Reports', 2)
    add_paragraph(doc, 'To create custom reports:')
    add_numbered_point(doc, 'Create QWeb report template')
    add_numbered_point(doc, 'Define report action in XML')
    add_numbered_point(doc, 'Add report to menu')
    add_numbered_point(doc, 'Test report generation')
    
    add_heading(doc, '9.4 Extending Email Templates', 2)
    add_paragraph(doc, 'To customize email notifications:')
    add_numbered_point(doc, 'Navigate to Settings → Technical → Email → Templates')
    add_numbered_point(doc, 'Duplicate existing template')
    add_numbered_point(doc, 'Modify subject and body')
    add_numbered_point(doc, 'Update model to use new template')
    
    doc.add_page_break()
    
    # 10. Troubleshooting
    add_heading(doc, '10. Troubleshooting', 1)
    
    add_heading(doc, '10.1 Common Issues', 2)
    
    add_paragraph(doc, 'Issue: Module not appearing in Apps list', bold=True)
    add_bullet_point(doc, 'Solution: Verify addons_path in odoo.conf')
    add_bullet_point(doc, 'Solution: Restart Odoo service')
    add_bullet_point(doc, 'Solution: Update Apps List')
    add_bullet_point(doc, 'Solution: Check file permissions')
    
    add_paragraph(doc, '\nIssue: Email notifications not sending', bold=True)
    add_bullet_point(doc, 'Solution: Configure outgoing mail server')
    add_bullet_point(doc, 'Solution: Test email configuration')
    add_bullet_point(doc, 'Solution: Check email template settings')
    add_bullet_point(doc, 'Solution: Verify recipient email addresses')
    
    add_paragraph(doc, '\nIssue: Trip number not generating', bold=True)
    add_bullet_point(doc, 'Solution: Check sequence configuration')
    add_bullet_point(doc, 'Solution: Verify sequence permissions')
    add_bullet_point(doc, 'Solution: Reset sequence if needed')
    
    add_paragraph(doc, '\nIssue: PDF reports not generating', bold=True)
    add_bullet_point(doc, 'Solution: Install wkhtmltopdf')
    add_bullet_point(doc, 'Solution: Configure wkhtmltopdf path')
    add_bullet_point(doc, 'Solution: Check report template syntax')
    
    add_heading(doc, '10.2 Log File Locations', 2)
    add_code_block(doc, '''/var/log/odoo/odoo-server.log - Main Odoo log
/var/log/postgresql/postgresql-13-main.log - Database log
/var/log/nginx/access.log - Web server access log
/var/log/nginx/error.log - Web server error log''')
    
    add_heading(doc, '10.3 Debug Mode', 2)
    add_paragraph(doc, 'Enable debug mode for troubleshooting:')
    add_numbered_point(doc, 'Navigate to Settings')
    add_numbered_point(doc, 'Click "Activate the developer mode"')
    add_numbered_point(doc, 'Access technical menu items')
    add_numbered_point(doc, 'View detailed error messages')
    
    add_heading(doc, '10.4 Database Backup', 2)
    add_paragraph(doc, 'Regular backup procedures:')
    add_code_block(doc, '''# Manual backup
pg_dump -U odoo -F c -b -v -f backup_$(date +%Y%m%d).dump odoo_db

# Automated daily backup (crontab)
0 2 * * * pg_dump -U odoo -F c -b -v -f /backups/odoo_$(date +%Y%m%d).dump odoo_db''')
    
    doc.add_page_break()
    
    # 11. API Reference
    add_heading(doc, '11. API Reference', 1)
    
    add_heading(doc, '11.1 Authentication', 2)
    add_paragraph(doc, 'API authentication using OAuth2 or API keys:')
    add_code_block(doc, '''# Using API key
curl -X GET "https://your-odoo-instance.com/api/fleet/vehicles" \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Using session authentication
curl -X POST "https://your-odoo-instance.com/web/session/authenticate" \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","params":{"db":"odoo_db","login":"user","password":"pass"}}'
''')
    
    add_heading(doc, '11.2 Transport Request API', 2)
    add_paragraph(doc, 'Create transport request:')
    add_code_block(doc, '''POST /api/fleet/transport-requests
{
  "requester_name": "John Doe",
  "department": "IT Department",
  "departure_date": "2024-02-15",
  "destination": "Pretoria",
  "purpose": "Meeting with stakeholders",
  "number_of_passengers": 3
}''')
    
    add_heading(doc, '11.3 Vehicle API', 2)
    add_paragraph(doc, 'Get vehicle availability:')
    add_code_block(doc, '''GET /api/fleet/vehicles/availability?date=2024-02-15&category=cat1
Response:
{
  "available_vehicles": [
    {"id": 1, "name": "VW Polo - ABC123GP", "category": "cat1"},
    {"id": 2, "name": "Toyota Etios - DEF456GP", "category": "cat1"}
  ]
}''')
    
    add_heading(doc, '11.4 Odometer Reading API', 2)
    add_paragraph(doc, 'Submit odometer reading:')
    add_code_block(doc, '''POST /api/fleet/odometer-readings
{
  "vehicle_id": 1,
  "reading": 45678,
  "reading_date": "2024-02-15",
  "fuel_level": "3/4",
  "notes": "Regular reading"
}''')
    
    doc.add_page_break()
    
    # 12. Maintenance & Updates
    add_heading(doc, '12. Maintenance & Updates', 1)
    
    add_heading(doc, '12.1 Regular Maintenance Tasks', 2)
    add_paragraph(doc, 'Daily:')
    add_bullet_point(doc, 'Monitor system logs for errors')
    add_bullet_point(doc, 'Check email notification queue')
    add_bullet_point(doc, 'Verify backup completion')
    
    add_paragraph(doc, '\nWeekly:')
    add_bullet_point(doc, 'Review pending approvals')
    add_bullet_point(doc, 'Check overdue trips')
    add_bullet_point(doc, 'Verify vehicle maintenance schedules')
    add_bullet_point(doc, 'Clean up old attachments')
    
    add_paragraph(doc, '\nMonthly:')
    add_bullet_point(doc, 'Database optimization (VACUUM)')
    add_bullet_point(doc, 'Review user access rights')
    add_bullet_point(doc, 'Update vehicle information')
    add_bullet_point(doc, 'Generate monthly reports')
    
    add_heading(doc, '12.2 Module Updates', 2)
    add_paragraph(doc, 'To update the module:')
    add_numbered_point(doc, 'Backup database before updating')
    add_numbered_point(doc, 'Download latest module version')
    add_numbered_point(doc, 'Replace module files')
    add_numbered_point(doc, 'Restart Odoo service')
    add_numbered_point(doc, 'Update module in Apps menu')
    add_numbered_point(doc, 'Test all functionality')
    
    add_heading(doc, '12.3 Database Optimization', 2)
    add_code_block(doc, '''# Vacuum and analyze database
psql -U odoo -d odoo_db -c "VACUUM ANALYZE;"

# Reindex database
psql -U odoo -d odoo_db -c "REINDEX DATABASE odoo_db;"

# Check database size
psql -U odoo -d odoo_db -c "SELECT pg_size_pretty(pg_database_size('odoo_db'));"''')
    
    add_heading(doc, '12.4 Performance Monitoring', 2)
    add_paragraph(doc, 'Monitor system performance:')
    add_bullet_point(doc, 'CPU usage (should be < 70%)')
    add_bullet_point(doc, 'Memory usage (should be < 80%)')
    add_bullet_point(doc, 'Disk I/O (monitor for bottlenecks)')
    add_bullet_point(doc, 'Database connections (monitor pool usage)')
    add_bullet_point(doc, 'Response times (should be < 2 seconds)')
    
    add_heading(doc, '12.5 Support & Contact', 2)
    add_paragraph(doc, 'For technical support:')
    add_bullet_point(doc, 'Email: support@ecdhs.gov.za')
    add_bullet_point(doc, 'Phone: +27 12 345 6789')
    add_bullet_point(doc, 'Documentation: https://docs.ecdhs.gov.za/fleet')
    add_bullet_point(doc, 'Issue Tracker: https://github.com/ecdhs/enhanced_fleet_management/issues')
    
    doc.add_page_break()
    
    # Appendix
    add_heading(doc, 'Appendix A: Configuration File Example', 1)
    add_code_block(doc, '''[options]
addons_path = /opt/odoo/addons,/opt/odoo/custom/addons
admin_passwd = CHANGE_ME
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = ^odoo_db$
http_port = 8069
logfile = /var/log/odoo/odoo-server.log
log_level = info
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200''')
    
    add_heading(doc, 'Appendix B: SQL Queries for Reporting', 1)
    add_code_block(doc, '''-- Vehicle utilization report
SELECT 
    v.name as vehicle,
    COUNT(ta.id) as total_trips,
    SUM(ta.distance_travelled) as total_distance,
    AVG(ta.distance_travelled) as avg_distance
FROM fleet_vehicle v
LEFT JOIN fleet_trip_authority ta ON ta.vehicle_id = v.id
WHERE ta.departure_date >= '2024-01-01'
GROUP BY v.id, v.name
ORDER BY total_trips DESC;

-- Pending approvals
SELECT 
    tr.name as request_number,
    rp.name as requester,
    tr.departure_date,
    tr.destination,
    tr.state
FROM fleet_transport_request tr
JOIN res_partner rp ON tr.requester_id = rp.id
WHERE tr.state IN ('submitted', 'dept_approved')
ORDER BY tr.departure_date;''')
    
    add_heading(doc, 'Appendix C: Glossary', 1)
    add_paragraph(doc, 'FML: Full Maintenance Lease - 60-month vehicle maintenance contract', bold=True)
    add_paragraph(doc, 'MM: Ministerial Maintenance - 120,000 KM maintenance contract for ministerial vehicles', bold=True)
    add_paragraph(doc, 'RT46: Official accident report form used by South African government', bold=True)
    add_paragraph(doc, 'GFMS: Government Fleet Management System - vehicle relief/replacement system', bold=True)
    add_paragraph(doc, 'Trip Authority: Official authorization document for vehicle usage', bold=True)
    add_paragraph(doc, 'Odometer Reading: Vehicle mileage measurement for tracking usage', bold=True)

    # Save document
    import os
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, 'Enhanced_Fleet_Management_Technical_Setup_Guide.docx')
    doc.save(output_path)
    print(f"✓ Technical & Setup Guide created successfully at: {output_path}")
    print("✓ Technical & Setup Guide created successfully!")

if __name__ == '__main__':
    create_technical_guide()
