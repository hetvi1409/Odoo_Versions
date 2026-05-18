{
    'name': "Asset Export Report",
    'description': """Asset Report: Asset Register Report""",
    'summary': """Property Reports""",
    'version': '19.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Services',
    'depends': ['asset_registry', 'account_asset'],
    'data': [
        'views/account_asset_views.xml',
        'wizard/asset_views.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
