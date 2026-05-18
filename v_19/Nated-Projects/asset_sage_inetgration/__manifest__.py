{
    'name': 'Fixed Asset Sage Inetgration',
    'category': 'Sales/Sign',
    'summary': """Fixed Asset Sage Inetgration""",
    'description': """Fixed Asset Sage Inetgration""",
    'version': '16.0.1.0.0',
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'account_accountant', 'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_sage_integration_views.xml',
        'views/account_account_views.xml',
    ],
    'images': [
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    # 'external_dependencies' : {
    #     'python' : ['pycryptodome'],
    # },
    'installable': True,
    'application': False,
    'auto_install': False,
}