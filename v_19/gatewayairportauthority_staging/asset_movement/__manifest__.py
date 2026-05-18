{
    'name': 'Asset Movement',
    'version': '19.0.0.0.0',
    'summary': 'Manage the addition of fixed assets movement',
    'description': """
        This module allows users to manage the addition of fixed assets movement, 
    """,
    'category': 'Accounting/Assets',
    'depends': ['account_asset', 'fixed_assets', 'asset_registry'],
    'data': [
        "security/ir.model.access.csv",
        "views/asset_movement_views.xml"
    ],
    'installable': True,
    'application': True,
}
