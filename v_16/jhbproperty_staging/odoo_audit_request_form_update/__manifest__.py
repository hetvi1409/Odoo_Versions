{
    'name': "Audit Request Form Update",
    'description': """Audit Request Form Update""",
    'summary': """Audit Request Form Update""",
    'version': '16.0.1.1.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Accounting',
    'depends': ['odoo_audit_request_form'],
    'data': [
        'data/audit_overview_data.xml',
        'security/ir.model.access.csv',
        'views/audit_request_views.xml',
        'views/audit_category_views.xml',
        'views/guidance_information_views.xml',
        'views/audit_overview_views.xml',
        'views/audit_dashboard.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/odoo_audit_request_form_update/static/src/scss/category.scss',
            '/odoo_audit_request_form_update/static/src/js/audit_dashboard.js',
            '/odoo_audit_request_form_update/static/src/xml/audit_dashboard.xml',
            '/odoo_audit_request_form_update/static/src/scss/audit_dashboard.scss',
            '/odoo_audit_request_form_update/static/src/js/lib/Chart.bundle.js',
        ]
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
