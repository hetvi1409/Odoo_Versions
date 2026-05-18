# -*- coding: utf-8 -*-
{
    "name": "Discuss Extension",
    "summary": "Discuss Extension",
    "version": "19.0.1.0.0",
    'category': 'Extra Tools',
    "description": """
		Discuss Extension 
		* add field [Partners with Need Action] in mail template
    """,
    'images': [
        'static/description/cover.png'
    ],
    "license": "OPL-1",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "installable": True,
    "depends": [
        'mail'
    ],
    "data": [
        'view/mail_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oi_mail/static/src/js/activity_group_view.js',
            'oi_mail/static/src/js/activity_group.js',
        ],
    },
    'installable': True,
    'odoo-apps': True,
    'auto_install': True,
}
