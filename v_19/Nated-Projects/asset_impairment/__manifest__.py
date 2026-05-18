{
    'name': "Asset Impairment",
    'description': """Asset Impairment""",
    'summary': """Asset Impairment""",
    'version': '16.1.0.0.0',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['account_asset','asset_registration','mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_cron.xml',
        'data/mail_templates.xml',
        'report/report.xml',
        'views/account_asset_views.xml',
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
