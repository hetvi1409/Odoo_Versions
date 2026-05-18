# -*- coding: utf-8 -*-

{
    'name': 'Sale List & Form Widget',
    'version': '1.9',
    'category': '',
    'sequence': 15,
    'summary': 'Sale',
    'website': 'https://www.odoo.com/app/crm',
    'depends': ['base','sale_management'],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        # web.assets_backend = all JS/CSS loaded in backend
        'web.assets_backend': [
            # 'sale_list_form_widget/static/src/js/priority_widget.js',
            # 'sale_list_form_widget/static/src/xml/priority_widget.xml',
            # 'sale_list_form_widget/static/src/scss/priority_widget.scss',

            'sale_list_form_widget/static/src/js/amount_range_widget.js',
            'sale_list_form_widget/static/src/xml/amount_range_widget.xml',
            'sale_list_form_widget/static/src/scss/amount_range_widget.scss',
        ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
