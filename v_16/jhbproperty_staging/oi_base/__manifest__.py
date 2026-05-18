# -*- coding: utf-8 -*-
{
    "name": "Base Extension",
    "summary": "Utilities functions for base model",
    "version": "16.0.1.1.35",
    'category': 'Extra Tools',
	"description": """
		Utilities functions for base model 
		 
    """,
	'images':[
        'static/description/cover.png'
	],
    "license": "OPL-1",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "installable": True,
    "depends": [
        'base', 'web'
    ],
    "data": [
        'view/ir_module_module.xml',
        'view/ir_rule.xml',
        'view/ir_ui_menu.xml',
        'view/ir_actions_server.xml',
        'view/ir_ui_view.xml',
        'view/ir_model_fields.xml',
        'view/action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oi_base/static/src/js/*.js',
            'oi_base/static/src/xml/*.xml'    
        ]
    },    
    'external_dependencies' : {
        'python' : ['unidecode'],
    },    
    'installable': True,
    'auto_install': True,    
    'odoo-apps' : True     
}

