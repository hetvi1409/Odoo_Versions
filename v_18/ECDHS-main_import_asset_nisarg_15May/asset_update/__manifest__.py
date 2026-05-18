{
    'name': " Asset Update",
    'description': """Asset Update""",
    'summary': """Asset Update""",
    'version': '18.0.1.0.0',
    'sequence': '20',
    'category': 'Services',
    'depends': ['accountant','account_asset',],
    'data': [
        'views/account_assets.xml',
        'views/hr_employee_views.xml'

    ],

    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
