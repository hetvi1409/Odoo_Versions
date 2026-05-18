{
    'name': "Budget Management Update",
    'description': """Budget Management Update""",
    'summary': """Budget Management Update""",
    'version': '19.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'category': 'Services',
    'depends': ['mail', 'account', 'account_budget', 'report_xlsx', 'account_accountant'],
    'data': [
        'data/ir_cron.xml',
        'data/mail_template.xml',
        'security/crossovered_budget_groups.xml',
        'views/crossovered_budget_views.xml',
        'report/budget_reports.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'budget_update/static/src/js/action_manager.js',
            ],
        },

    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
