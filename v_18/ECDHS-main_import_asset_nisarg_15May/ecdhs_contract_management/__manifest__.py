# -*- coding: utf-8 -*-
# Eastern Cape Department of Human Settlements
# Procurement Contract Management – Odoo v18

{
    'name': 'ECDHS Contract Management',
    'version': '18.0.1.0.8',
    'category': 'Services/Contract Management',
    'summary': 'Procurement contract lifecycle management aligned to the ECDHS PFMA SOP',
    'description': """
Eastern Cape DSD – Contract Management Process
===============================================
Implements the Standard Operating Procedure (SOP-CONTRACT-MANAGEMENT-01) for
managing Service Level Agreements, Lease Agreements and Cessions.
xe
Legislative basis
-----------------
  * Constitution of the Republic of South Africa, Section 217
  * Public Finance Management Act No. 1 of 1999 (PFMA), as amended
    """,
    'author': 'ECDHS',
    'website': 'https://www.ecdsd.gov.za',
    'license': 'LGPL-3',
    'icon': '/ecdhs_contract_management/static/description/icon2.png',
    'image': '/ecdhs_contract_management/static/description/icon2.png',
    'depends': [
        'base',
        'mail',
        'account',
        'hr',
        'portal',
        'sign',
                'xf_partner_contract',
                'e_system',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/contract_template_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'data/dashboard_data.xml',
        'views/portal_contract.xml',
        'views/report_contract_document.xml',
        'wizard/contract_terminate_wizard_views.xml',
        'wizard/contract_verify_warning_wizard_views.xml',
        'views/ecdhs_contract_addendum_views.xml',
        'views/ecdhs_contract_payment_views.xml',
        'views/ecdhs_contract_monitoring_views.xml',
        'views/ecdhs_contract_template_views.xml',
        'views/ecdhs_contract_views.xml',
        'views/memo_contract_link_views.xml',
        'views/ecdhs_contract_dashboard_views.xml',
        'views/ecdhs_contract_version_views.xml',
        'views/ecdhs_mail_template_preview_views.xml',
        'wizard/contract_request_changes_wizard_views.xml',
        'views/sign_send_request_views.xml',
        'views/sign_thank_you_page.xml',
        'views/sign_refuse_button_left.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ecdhs_contract_management/static/src/css/chatter_buttons_fix.css',
            'ecdhs_contract_management/static/src/css/contract_dashboard.css',
            'ecdhs_contract_management/static/src/xml/searchable_role_dialog.xml',
            'ecdhs_contract_management/static/src/js/searchable_role_dialog.js',
            'ecdhs_contract_management/static/src/js/restrict_contract_sign_roles.js',
        ],
        'sign.assets_public_sign': [
            'ecdhs_contract_management/static/src/css/sign_validate_button.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
