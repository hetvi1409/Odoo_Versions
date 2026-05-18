{
    'name': "Servitude Register",
    'description': """Servitude Register""",
    'summary': """Servitude Register""",
    'version': '16.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Services',
    'depends': ['itsys_real_estate', 'property_update'
                ],
    'data': [
        'data/mail_template_data.xml',
        'data/ir_corn_data.xml',
        'security/servitude_register_groups.xml',
        'security/ir.model.access.csv',
        'views/serviitude_register_views.xml',
        'views/res_config_settings_views.xml',
        'views/building_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
