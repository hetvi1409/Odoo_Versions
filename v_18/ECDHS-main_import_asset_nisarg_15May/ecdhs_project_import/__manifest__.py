{
    'name': "ECDHS Project Import",
    'description': """ECDHS Project Import""",
    'summary': """ECDHS Project Import""",
    'version': '18.0.1.1.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['base','project','project_account_budget'],
    'data': [
        'wizard/project_import_views.xml',
        'views/project_views.xml',
        'security/ir.model.access.csv'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
