# -*- coding: utf-8 -*-
{
    'name': "Property Management",
    'version': '18.0.3.1.0',
    "summary": "Property Management",
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za",
    "depends": ["base", "web", "auth_signup", "website", "itsys_real_estate",
                "crm"],
    "data": [
        'data/ir_sequence_data.xml',
        "security/ir.model.access.csv",
        "report/rental_contract_sign_report.xml",
        "report/rental_contract_report.xml",
        "views/rental_contract_views.xml",
        "views/signup_template_views.xml",
        "views/res_district_views.xml",
        "views/crm_lead_views.xml",
        # "views/lease_agreement_views.xml",
        'views/property_enquiry_templates.xml',
        "views/website_building_templates.xml",
        "views/res_partner_views.xml",
        "views/sign_template_views.xml",
        "views/ownership_contract_views.xml",
        "views/res_conf_settings_views.xml",
        "views/property_interset_views.xml",
        "wizard/crm_lead2opportunity_partner_views.xml",
    ],

    'assets': {
        'web.assets_frontend': [
            "/real_estate_management/static/src/js/property_enquiry.js"
        ]
    },
    'qweb': [],
    'images': [],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
