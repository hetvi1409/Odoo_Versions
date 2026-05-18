# -*- coding: utf-8 -*-
{
    'name': "Sale-Invoice Customizations",

    'summary': "Sale Order, Invoice Customizations",

    'description': """
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'General',
    'version': '18.0.1.0.0',

    'depends': ['base', 'sale_management', 'account'],

    'data': [
        'data/partner_sequence.xml',
        'views/res_partner.xml',
        'views/sale_order_inherited_view.xml',
        'views/account_move_inherited_view.xml',
    ],
}
