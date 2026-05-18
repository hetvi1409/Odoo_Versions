# -*- coding: utf-8 -*-
{
    'name': "Approval Sign",
    'description': """Approval Sign""",
    'summary': """Approval Sign""",
    'version': '16.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Services',
    'depends': ['base', 'web','approvals'],
    'data': [
        'views/res_company.xml',
        'views/custom_external_layout.xml',
        'views/approval_report.xml',
        'views/approval_report_template.xml',
        'views/approval_views.xml'
    ],
    'assets': {
        'web.assets_common': [
            'approval_sign/static/img/COJ_Logo1.png',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}

