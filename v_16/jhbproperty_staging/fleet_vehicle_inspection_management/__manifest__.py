# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author:Anjhana A K(<https://www.cybrosys.com>)
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Vehicle Inspection Management in Fleet',
    'version': '16.0.1.0.0',
    'category': 'Industries',
    'summary': """Vehicle Inspection Management for managing the Vehicle
    Inspection and services""",
    'description': """Efficiently organize and oversee vehicle inspections and
    services with  Vehicle Inspection Management system in Odoo, ensuring
    optimal functionality and maintenance""",
    'depends': ['base', 'fleet', 'mail', 'hr'],
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'images': ['static/description/banner.jpg'],
    'website': 'https://www.cybrosys.com',
    'data': [
        'security/vehicle_inspection_access.xml',
        'security/vehicle_inspection_management_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'data/fleet_vehicle_master_data.xml',
        'data/fleet_inspection_request_data.xml',
        'data/fleet_employee_data.xml',
        'data/fleet_policy_data.xml',
        'data/fleet_vehicle_request_data.xml',
        'data/fleet_after_hours_data.xml',
        'data/fleet_key_register_data.xml',
        'data/fleet_job_card_data.xml',
        'data/fleet_fuel_register_data.xml',
        'data/fleet_trip_log_data.xml',
        'data/fleet_daily_checklist_data.xml',
        'data/fleet_service_logbook_data.xml',
        'data/fleet_accident_report_data.xml',
        'views/vehicle_inspection_views.xml',
        'views/fleet_documents_menus.xml',
        'views/inspection_request_views.xml',
        'wizards/fleet_service_inspection_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/fleet_vehicle_log_services_views.xml',
        'views/vehicle_service_log_views.xml',
        'views/vehicle_request_views.xml',
        'views/after_hours_authorization_views.xml',
        'views/key_register_views.xml',
        'views/accident_report_views.xml',
        'views/policy_document_views.xml',
        'views/job_card_views.xml',
        'views/fuel_register_views.xml',
        'views/trip_log_views.xml',
        'views/daily_checklist_views.xml',
        'views/service_logbook_views.xml',
        'reports/vehicle_inspection_reports.xml',
        'reports/vehicle_inspection_report_templates.xml',
        'reports/fleet_documents_reports.xml',
        'reports/job_card_report_templates.xml',
        'reports/trip_log_report_templates.xml',
        'reports/accident_report_templates.xml',
        'reports/vehicle_request_report_templates.xml',
        'reports/after_hours_report_templates.xml',
        'reports/key_register_report_templates.xml',
        'reports/fuel_register_report_templates.xml',
        'reports/daily_checklist_report_templates.xml',
        'reports/service_logbook_report_templates.xml',
        'reports/policy_document_report_templates.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
