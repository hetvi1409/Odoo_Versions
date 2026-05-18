# -*- coding: utf-8 -*-
{
    'name': "Field Selection Configuration",

    'summary': """Change field selection options from Odoo interface, Field Configuration, Database Structure, Custom Module""",

    'description': """
        Change field selection options from odoo interface without need a custom module
    """,

    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "license": "OPL-1",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'oi_base'],

    # always loaded
    'data': [
        'view/ir_model_fields.xml',
        'view/ir_model_fields_selection.xml',
        'security/ir.model.access.csv'
    ],
    
    'external_dependencies' : {
        
    },
    'odoo-apps' : True,
    'auto_install': True,
    'images':[
        'static/description/cover.png'
    ]     
}
