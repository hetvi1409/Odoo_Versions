# -*- coding: utf-8 -*-
#################################################################################
# Author      : Terabits Technolab (<www.terabits.xyz>)
# Copyright(c): 2022,23
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': "Law Firm Management | Case Management for Lawyers and Law Firms | Law Firm Management System | Legal Case & Matter management | Law Practice Management",
    'version': "19.0.1.0.0",
    'summary': """
Law Firm Management - Manage your cases, to-dos, hearings, invoices, cause list, matters, etc. Try it today!,
Legal Case & Matter management,
Legal Case Management,
Law Firm ERP,
Legal & Law Practice Management,
Law ERP Module,
Manage Law Cases App,
Law Matter Management System,
Track Law Cases With Full Step,
Handle Law Acts, Law Articles Management Odoo,
Advocate Cases and Hearings Management for Law Firm.""",
    'sequence': 7,
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'description': """
        Law Firm Management is a product of the digital age, purpose-designed for lawyers, law firms, and legal departments. The module provides solutions to the challenges faced in organizing, streamlining, and effectively utilizing the dynamic information that advocates and law firms handle each day. It empowers you and/or your team to be even more efficient, saves you a lot of time, and enhances team collaboration as well as client and advocate relationships. It can serve as your virtual office, allowing you to allocate work, take notes, check hearing dates and keep tabs on teamwork anywhere, anytime from an internet-enabled device.
    """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': [
        'project', 'hr_expense', 'calendar', 'hr_timesheet', 'crm', 'helpdesk', 'timesheet_grid'
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'data': [
        'data/sequence.xml',
        'data/default_data.xml',
        'data/legal_subtype_data.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/view_tasks.xml',
        'views/view_matters.xml',
        'views/view_cases.xml',
        'views/view_court.xml',
        'views/view_judge.xml',
        'views/view_res_partner.xml',
        'views/view_trust_account.xml',
        'views/view_calendar.xml',
        'views/view_crm_lead.xml',
        'views/view_law_task_list.xml',
        'views/view_hr_employee.xml',
        'views/view_account_move.xml',
        'views/view_crime_type.xml',
        'wizard/view_wizard_law_close_reason.xml',
        'wizard/view_wizard_consultation_invoice.xml',
        'wizard/view_wizard_create_law_invoice.xml',
        'wizard/view_wizard_invoice_deduction.xml',

        'views/helpdesk_ticket_view.xml',
        'views/menu_items.xml',
        'views/view_legal_subtype.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'law_firm_bits/static/src/js/plugins/chartjs_min.js',
            'law_firm_bits/static/src/xml/dashboard_view.xml',
            'law_firm_bits/static/src/scss/dashboard_view.css',
            'law_firm_bits/static/src/js/dashboard_view.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
}
