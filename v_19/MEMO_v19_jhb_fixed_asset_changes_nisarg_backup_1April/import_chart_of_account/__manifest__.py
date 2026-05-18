{
    'name': "Import Chart of Account",
    'description': """Import Chart of Account""",
    'summary': """Import Chart of Account""",
    'version': '19.0.1.1.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'wizard/account_account_import_views.xml',
        'views/account_account_views.xml',
        'views/account_category_views.xml',
        'security/ir.model.access.csv'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
