# -*- coding: utf-8 -*-
{
    'name': "Property Management",
    'version': '18.0.2.0.0',
    "summary": "Property Management",
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za",
    "depends": ["base", "web", "auth_signup", "website", "itsys_real_estate"],
    "data": [
        'data/ir_sequence_data.xml',
        'data/mail_template_enquiry_data.xml',
        "security/ir.model.access.csv",
        "security/property_management_system_security.xml",

        "views/signup_template_views.xml",
        "views/res_district_views.xml",
        "views/property_enquiry_views.xml",
        'views/property_enquiry_templates.xml',
        "views/portal_property_enquiry_views.xml",
        "views/website_building_templates.xml",
        "views/building_views.xml",
        "views/res_partner_views.xml",
        "views/property_buy_rent_template.xml",
        "views/property_snippet_templates.xml",
        "views/property_overview_templates.xml",

        "wizard/tenant_mix_criteria_views.xml",

        "views/property_management_system_menus.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            '/property_management_system/static/src/js/property_enquiry.js',
            '/property_management_system/static/src/js/property_buy_rent.js',
            '/property_management_system/static/src/scss/property.scss',
            '/property_management_system/static/src/scss/snippet.scss'
            ],
        'web.assets_backend': [
            '/property_management_system/static/src/scss/property_enquiry.scss',
        ],
    },
    'qweb': [],
    'images': [],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
