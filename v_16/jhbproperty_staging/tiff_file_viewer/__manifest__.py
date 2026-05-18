# -*- coding: utf-8 -*-
{
    'name': 'TIFF Image Preview',
    'version': '16.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'category': 'Extra Tools',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'tiff_file_viewer/static/src/xml/binary_widget.xml',
            'tiff_file_viewer/static/src/js/binary_widget.js',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        "wizard/image_preview_views.xml"
    ],
    "external_dependencies": {"python": [
        "filetype",
    ]},
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
