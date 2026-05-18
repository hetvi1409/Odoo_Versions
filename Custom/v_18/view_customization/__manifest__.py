# -*- coding: utf-8 -*-
{
    'name': "views customization",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale_management','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'views/sale_order.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'view_customization/static/src/js/kanban_view.js',
            'view_customization/static/src/js/sale_order.js',

            'view_customization/static/src/js/sale_systray.js',
            'view_customization/static/src/xml/sale_systray.xml',

            'view_customization/static/src/js/sale_delete_confirm.js',


            'view_customization/static/src/js/amount_color.js',
            'view_customization/static/src/xml/amount_color.xml',

        ],
    },
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

