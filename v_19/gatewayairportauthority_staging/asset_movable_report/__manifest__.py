{
    'name': 'Asset Movable Report',
    'version': '19.0.0.0.0',
    'category': 'Assets',
    'summary': 'Print PDF showing asset names and barcodes from menu',
    'depends': ['account_asset', 'web', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_templates.xml',
        'report/movable_asset_report.xml',
        'wizard/asset_movable_report_views.xml',
        # 'views/asset_movable_report_menus.xml',
    ],
    'installable': True,
    'application': False,
}
