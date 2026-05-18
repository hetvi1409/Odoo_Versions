# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Enhanced Fleet Management',
    'version': '18.0.2.0.0',
    'category': 'Human Resources/Fleet',
    'summary': 'Comprehensive Fleet Management with Forms, Accident Reporting, Relief Management, and Odometer Tracking',
    'description': """
Enhanced Fleet Management Module
=================================
This module extends the standard Odoo Fleet Management with:
* Transport Request Management
* Trip Authority Forms
* Vehicle Checklists (Pre/Post Trip)
* Lost and Theft Reporting
* Accident Reports (RT46 Form)
* Vehicle Relief Management
* Odometer Reading Tracking
* Comprehensive Reports and Printing
* Process Flow Automation
    """,
    'author': 'ECDHS',
    'website': 'https://www.ecdhs.org',
    'depends': [
        'base',
        'fleet',
        'hr',
        'mail',
        'web',
    ],
    'data': [
        # Security
        'security/fleet_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence_data.xml',
        'data/mail_template_data.xml',

        # Views - Order matters for cross-references
        'views/fleet_trip_authority_views.xml',
        'views/fleet_transport_request_views.xml',
        'views/fleet_vehicle_checklist_views.xml',
        'views/fleet_lost_theft_views.xml',
        'views/fleet_accident_report_views.xml',
        'views/fleet_vehicle_relief_views.xml',
        'views/fleet_odometer_reading_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/fleet_menu_views.xml',

        # Reports
        'report/fleet_reports.xml',
        'report/transport_request_report_template.xml',
        'report/trip_authority_report_template.xml',
        'report/vehicle_checklist_report_template.xml',
        'report/lost_theft_report_template.xml',
        'report/accident_report_template.xml',
        'report/vehicle_relief_report_template.xml',
        'report/odometer_reading_report_template.xml',

        # Wizards
        'wizard/fleet_report_wizard_views.xml',

        # Demo Data
        # 'data/demo_data.xml',
        'data/demo_data_v18_complete.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'enhanced_fleet_management/static/src/css/fleet_management.css',
            'enhanced_fleet_management/static/src/js/fleet_dashboard.js',
            'enhanced_fleet_management/static/src/xml/fleet_dashboard.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'demo': [
        # 'data/demo_data.xml',
        'data/demo_data_v18_complete.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
