{
    'name': 'Asset Disposal',
    'version': '19.0.1.0.0',
    'summary': 'Manage the disposal of fixed assets including calculations and journal entries',
    'description': """
        This module allows users to manage the disposal of fixed assets, including handling different disposal methods (Sale, Donation, Scrapping, Other), calculating depreciation, and generating necessary journal entries.
    """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'category': 'Accounting/Assets',
    'depends': ['account_asset'],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'data/data.xml',
        'views/asset_modify_views.xml',
        # 'views/asset_disposal_views.xml',
        # 'views/asset_disposal_menus.xml',
        # 'data/disposal_journal_entries.xml',
        # 'report/asset_disposal_audit.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}
