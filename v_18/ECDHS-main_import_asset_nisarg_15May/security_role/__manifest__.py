# -*- coding: utf-8 -*-
{
    'name': "User Roles",
    'description': """User Roles""",
    'summary': """User Roles""",
    'version': '18.0.1.0.0',
    'sequence': '20',
    'category': 'Services',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/user_role_views.xml',
        'views/res_users_views.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
