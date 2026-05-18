# -*- coding: utf-8 -*-
{
    'name': "Emergency Housing Management",
    'version': '18.0.1.0.0',
    "summary": "Emergency Housing Management",
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za",
    "depends": ["mail", "xf_partner_contract", 'web', "website_housing_subsidy", "hr"],
    "data": [
        'data/ir_sequence_data_views.xml',
        'data/house_settlement_data.xml',
        'security/emergency_housing_security.xml',
        'security/ir.model.access.csv',
        'views/emergency_housing_views.xml',
        'views/emergency_housing_templates_views.xml',
        'views/house_settlement_views.xml',
        'views/res_country_city_views.xml',
        'wizard/review_message_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/emergency_housing/static/src/css/emergency_housing.scss',
            # '/emergency_housing/static/src/js/application.js',
        ],
    },
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
