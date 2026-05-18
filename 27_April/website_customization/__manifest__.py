# -*- coding: utf-8 -*-
{
    'name': 'Website Customization',
    'version': '18.0.1.0.0',
    'author': 'unknown',
    'category': 'website',
    'description': 'Website Customization',
    'website': '',
    'depends': ['base', 'website','website_sale','stock','crm'],
    'data': [
        'views/inquiry_template.xml',
        'views/menu.xml',
        'views/hide_price.xml',
        # 'views/shop_filter.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_customization/static/src/js/website_sale.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}