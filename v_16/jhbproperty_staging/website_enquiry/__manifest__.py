{
    'name': "Enquiry Website",
    'description': """Client Enquiry Website""",
    'summary': """Client Enquiry Website""",
    'version': '16.0.0.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Services',
    'depends': ['website', 'auth_signup'],
    'data': [
        'views/webclient_templates.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'website_enquiry/static/src/scss/website_layout.scss'
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
