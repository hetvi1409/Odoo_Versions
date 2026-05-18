{
    'name': "Housing Subsidy",
    'description': """Housing Subsidy""",
    'summary': """housing subsidy application""",
    'version': '18.0.1.0.0',
    'category': 'Services',
    'depends': ['base', 'website','xf_partner_contract'],
    'data': [
        'data/mail_template_data.xml',
        'data/res_race.xml',
        'data/subsidy_sequence.xml',
        'views/housing_subsidy_views.xml',
        'security/subsidy_security.xml',
        'security/ir.model.access.csv',
        'views/housing_subsidy_template.xml',
        'views/res_race_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_housing_subsidy/static/src/js/housing_subsidy.js',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
