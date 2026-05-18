{
    'name': "Asset Dashboard",
    'description': """Asset Dashboard""",
    'summary': """Asset Dashboard""",
    'version': '18.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['base', 'account_asset', 'asset_verification','fixed_assets'],
    'data': [
        'security/security.xml',
        'views/account_asset_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'asset_dashboard/static/src/xml/asset_dashboard.xml',
            'asset_dashboard/static/src/js/asset_dashboard.js',
            'asset_dashboard/static/src/scss/asset_dashboard.scss',
            'asset_dashboard/static/src/js/lib/Chart.bundle.js'
            # 'asset_verification/static/src/css/asset_verification_style.scss'
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

}
