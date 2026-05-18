{
    'name': 'Asset Addition',
    'version': '18.0.1.0.0',
    'summary': 'Manage the addition of fixed assets ',
    'description': """
        This module allows users to manage the addition of fixed assets, 
    """,
    'category': 'Accounting/Assets',
    'depends': ['account_asset', 'fixed_assets', 'asset_registry'],
    'data': [
        "data/asset_addition_data.xml",
        "data/mail_template_data.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/asset_addition_views.xml",
        "views/asset_removal_views.xml",
        "views/account_assets_views.xml",
        "views/asset_verification_views.xml"
    ],
    'installable': True,
    'application': True,
}
