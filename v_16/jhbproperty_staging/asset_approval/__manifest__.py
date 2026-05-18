{
    'name': "Asset Approval",
    'description': """Asset Approval""",
    'summary': """Asset Approval""",
    'version': '16.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['base', 'account_asset'],
    'data': [
        'security/security_groups.xml',
        'data/mail_templates.xml',
        'views/account_asset.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,

}