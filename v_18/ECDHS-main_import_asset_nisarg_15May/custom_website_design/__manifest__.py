{
    'name': "Website Design",
    'description': """Website Design""",
    'summary': """Website Design""",
    'version': '18.0.1.0.0',
    'category': 'Theme/eCommerce',
    'depends': ['website', 'base', 'web'],
    'data': [
        'data/website_data.xml',
        'views/eastern_homepage.xml',
        'views/website_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_website_design/static/src/js/home_page.js',
            'custom_website_design/static/src/css/style.css',
        ],
        'web.assets_backend': [
            'custom_website_design/static/src/scss/custom_style.scss',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
