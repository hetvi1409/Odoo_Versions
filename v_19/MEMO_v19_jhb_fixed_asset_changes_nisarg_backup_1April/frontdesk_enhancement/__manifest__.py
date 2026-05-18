# -*- coding: utf-8 -*-
{
    'name': "Frontdesk Enhancement",
    'version': '19.0.1.0.0',
    "summary": "The module unifies Visitors, Contractors, and Device/Laptop registrations into a single model and form",
    'category': 'Services',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za/",
    "depends": ["base", "frontdesk", "web"],
    "data": [
        'data/ir_sequence_data.xml',
        'views/frontdesk_visitor_views.xml'
    ],
    # 'assets': {
    #     'frontdesk.assets_frontdesk': [
    #         ('remove', 'frontdesk/static/src/host_page/host_page.xml'),
    #         # "frontdesk_enhancement/static/src/host_page/host_page.xml",
    #         ('remove', 'frontdesk/static/src/host_page/host_page.js'),
    #         # "frontdesk_enhancement/static/src/host_page/host_page.js",
    #         'frontdesk_enhancement/static/src/**/*',
    #     ],
    #
    # },
    'qweb': [],
    'images': [],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
