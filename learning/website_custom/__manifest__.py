# -- coding: utf-8 --
{
    'name': "Website Customization",
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': """Website customization""",
    'description': """Website customization""",
    'author': 'unknown',
    'company': 'unknown',
    'maintainer': 'unknown',
    'website': "https://www.unknown.com",
    'depends': ['website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_template.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 'website_custom/static/src/css/website_custom.css',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
