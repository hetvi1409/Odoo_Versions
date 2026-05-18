# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Discuss Extension",
    "summary": "Discuss Extension",
    "version": "18.0.1.0.0",
    'category': 'Extra Tools',
    "website": "https://www.open-inside.com",
	"description": """
		Discuss Extension 
		* add field [Partners with Need Action] in mail template
    """,
	'images':[
        'static/description/cover.png'
	],
    "author": "Openinside",
    "license": "OPL-1",
    "price" : 9.99,
    "currency": 'USD',
    "installable": True,
    "depends": [
        'mail'
    ],
    "data": [
        'view/mail_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'oi_mail/static/src/js/activity_group_view.js',
            # 'oi_mail/static/src/js/activity_group.js',
        ],
    },     
    'installable': True,
    'odoo-apps' : True,
    'auto_install' : True,
}

