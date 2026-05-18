# -*- coding: utf-8 -*-
{
    'name': 'Smart Contract Dashboard',
    'version': '1.9',
    'category': '',
    'sequence': 15,
    'summary': 'Darshboards',
    'website': 'https://www.odoo.com/app/crm',
    'depends': ['base','sale_management'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_actions_client.xml',
    ],
    # 'demo': [
    #     'data/crm_team_demo.xml',
    # ],
    'installable': True,
    'application': True,
     'assets': {
          'web.assets_backend': [
                'smart_contact_dashboard/static/src/**/*',
          ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}



