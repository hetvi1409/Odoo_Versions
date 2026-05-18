# -*- coding: utf-8 -*-
{
    'name': "Library Management OWL",
    'summary': "Library Management Module using OWL framework",
    'description': """Library Management Module using OWL framework""",
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': ['base','web'],

    'data': [
        'security/ir.model.access.csv',
        'views/library_book.xml',
        'views/ir_actions_client.xml',
    ],
    "assets": {
        'web.assets_backend': [
            'library_management_owl/static/src/js/client_action/library_dashboard.js',
            'library_management_owl/static/src/js/client_action/template.xml',
        ],
    },

}

