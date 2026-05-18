{
    'name': "Asset Registry",
    'description': """Asset Registry""",
    'summary': """Asset Registry""",
    'version': '19.0.1.0.0',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['base', 'account_asset','account','hr'],
    'data': [
            'security/ir.model.access.csv',
            'views/account_asset_views.xml',
            'views/asset_category.xml',
            # 'views/asset_location.xml',
            'views/res_config_settings.xml',
            'views/asset_verification_job_building.xml',
            'wizard/asset_import_views.xml',
        ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

}