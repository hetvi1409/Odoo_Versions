# -*- coding: utf-8 -*-
{
    "name": "Client Action Refresh",
    "summary": "Refresh, Reload, Auto Refresh, Auto Reload, Client",
    "version": "16.0.1.1.4",
    'category': 'Extra Tools',
	"description": """
		Client Action Refresh 
    """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
	'images':[
        'static/description/cover.png'
	],
    "license": "OPL-1",
    "installable": True,
    "depends": [
        'web'
    ],
    "data": [
        
    ],    
    'installable': True,
    'auto_install': True,    
    'odoo-apps' : True,
    'images':[
        'static/description/cover.png'
    ],       
    'assets': {
        'web.assets_backend': [
            'oi_action_trigger_reload/static/src/js/pager.js',
            'oi_action_trigger_reload/static/src/js/trigger_reload.js',
            'oi_action_trigger_reload/static/src/js/action_menu.js',
        ],

    },         
}

