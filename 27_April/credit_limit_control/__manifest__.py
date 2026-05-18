# -*- coding: utf-8 -*-
{
    'name': 'Credit Limit Control Syatem',
    'version': '18.0.1.0.0',
    'author': 'unknown',
    'category': 'sale',
    'description': 'Credit Limit Control Syatem',
    'website': '',
    'depends': ['base', 'sale_management','accountant'],
    'data': [
        'views/res_partner.xml',
        'security/res_groups.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}