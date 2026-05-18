{
    'name': "Fixed Assets",
    'description': "Fixed Assets",
    'summary': "Fixed Assets",
    'version': '19.0.0.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': 20,
    'depends': [
        'asset_registry',
        'account_asset',
        'accountant',
        'asset_verification',
        'assets_disposal'
    ],
    'category': 'Services',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/asset_removal_wizard.xml',
        'views/assets_views.xml'
    ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
