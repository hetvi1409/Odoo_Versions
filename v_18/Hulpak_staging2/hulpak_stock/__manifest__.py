# -*- coding: utf-8 -*-

{
    'name': 'Delivery and Reports',
    'version': '18.0.1.0.0',
    'category': 'Warehouse',
    'summary': """Generating Certificate of Conformity (Coc) for deliveries""",
    'description': """This module facilitates the creation Coc""",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'http://natedsystetems.co.za',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_move.xml',
        'report/stock_picking_templates.xml',
        'report/stock_picking_reports.xml',
        'report/stock_picking_report_template.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
