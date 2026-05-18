# -*- coding: utf-8 -*-
{

    'name': "My Home",
    'version': '16.0.1.0.0',
    "summary": "Access all app from my home",
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za",
    "depends": ["base", "account", "auth_oauth","auth_signup","e_system","web","website",],
    "data": [
        "views/portal_template.xml",
        "views/website_layout.xml",
    ],
    'qweb': [],
    'images': [],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
