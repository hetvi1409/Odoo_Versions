# -*- coding: utf-8 -*-
{
    'name': 'Access Roles',
    'version': '18.0.1.0.0',
    'category':'Security',
    'sequence': 1,
    'summary': 'Access Roles for users',
    'description': """Access Roles for users""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'mail', 'web'],
    'data': [
            'security/access_roles_security.xml',
            'security/ir.model.access.csv',
            'views/access_role_views.xml',
            'views/res_users_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

