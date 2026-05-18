# -*- coding: utf-8 -*-
{
    'name': "Property Intelligence",
    'description': """Property Intelligence""",
    'summary': """Property Intelligence""",
    'version': '16.0.2.1.1',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Services',
    'depends': ['base', 'property_update', 'client_enquiry', 'approvals'],
    'data': [
        'security/property_intelligence_security.xml',
        'views/client_enquiry_sla_policy_status.xml',
        'security/ir.model.access.csv',
        'views/property_intelligence_views.xml',
        'views/approval_views.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
