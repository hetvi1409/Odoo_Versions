# -*- coding: utf-8 -*-
{
    'name': "IP Future",
    'summary': "Short summary of module's purpose",
    'description': """
Long description of module's purpose
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','sale_management','purchase','accountant'],
    'data': [
        "views/sale_order_line.xml",
        "views/account_move_line.xml",
        "views/purchase_order.xml",
        "reports/account_report.xml",
    ],

}

