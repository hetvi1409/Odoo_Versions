{
    'name': 'Asset Useful Life Management',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Manage asset useful life and depreciation adjustments',
    'description': """
        This module manages the remaining useful life of assets and allows adjustments to the depreciation calculation.
    """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': ['account', 'account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/account_asset_adjust_life_wizard_views.xml',
        'views/account_asset_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
