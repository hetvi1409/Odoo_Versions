# -*- coding: utf-8 -*-
{
    'name': 'Module customization',
    'version': '18.0.1.0',
    'description': 'Custom module',
    'summary': 'Custom module',
    'author': '',
    'website': 'https://www.odoo.com/',
    'depends': ['base','purchase','event','mrp','website','mrp_workorder','sale_management','stock'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/purchase_order_view.xml',
        'views/portal_template.xml',

        'views/sale_order.xml',
    ],
    'installable': True,
    'application': True,
}