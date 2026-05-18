{
    'name': "Property Report",
    'description': """Property Report: Property Asset Register Report""",
    'summary': """Property Reports""",
    'version': '19.0.1.0.0',
    'sequence': '20',
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': ['itsys_real_estate', 'property_update'],
    'data': [
        'views/building_views.xml',
        'views/outdoor_advertisement_views.xml',
        'report/property_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'property_report/static/src/js/action_manager.js',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
