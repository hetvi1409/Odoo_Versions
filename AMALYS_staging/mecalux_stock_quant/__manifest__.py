# -*- coding: utf-8 -*-
{
    'name': "Mecalux Stock Quant",

    'summary': "Import stock quants from Mecalux",

    'description': """
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Inventory',
    'version': '18.0.1.0.0',

    'depends': ['base', 'stock'],

    'data': [
        "security/ir.model.access.csv",
        'data/server_action.xml',
        'wizards/mecalux_quant_format_wizard_view.xml',
    ],
}
