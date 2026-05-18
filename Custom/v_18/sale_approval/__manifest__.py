# -*- coding: utf-8 -*-
{
    'name': 'Sale Approval',
    'version': '18.0.1.0.0',
    'author': 'unknown',
    'category': 'Sales',
    'description': 'Sale Approval',
    'website': '',
    'depends': ['base', 'sale_management', 'stock'],
    'data': [
        'security/res_groups.xml',
        'views/sale_order.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'website_customization/static/src/js/website_sale.js'
    #     ]
    # },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}