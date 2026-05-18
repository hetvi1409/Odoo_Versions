# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Base Extension",
    "summary": "Utilities functions for base model",
    "version": "18.0.1.0.0",
    'category': 'Extra Tools',
    "website": "https://www.open-inside.com",
	"description": """Utilities functions for base model 
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
            # 'oi_base/static/src/js/debug_items.js',
            # 'oi_base/static/src/js/action_menu.js',
            # 'oi_base/static/src/js/record_info.js',
            # 'oi_base/static/src/js/rpc_service.js',
            # 'oi_base/static/src/js/*.js',
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

