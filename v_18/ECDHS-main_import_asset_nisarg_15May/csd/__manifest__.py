{
    'name': "CSD",
    'description': """CSD""",
    'summary': """CSD""",
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'depends': ['base','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/csd_sage_views.xml',
        'views/res_partner_views.xml',

    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
