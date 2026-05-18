# -*- coding: utf-8 -*-
{
    'name': "IP Astico",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
Long description of module's purpose
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','sale_management','accountant','stock'],

    'data': [
        'views/sale_order_line.xml',
        'views/account_move_line.xml',

        'reports/sale_order_report.xml',
        'reports/invoice_report.xml',
    ],
}

