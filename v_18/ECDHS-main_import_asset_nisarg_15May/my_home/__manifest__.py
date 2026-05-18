# -*- coding: utf-8 -*-
{

    'name': "My Home",
    'version': '18.0.1.0.0',
    "summary": "Access all app from my home",
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za",
    "depends": ["base", "portal", "account", "project"],
    "data": [
        "views/my_home_menu.xml",
    ],
    'qweb': [],
    'images': ['static/description/home.png'],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
