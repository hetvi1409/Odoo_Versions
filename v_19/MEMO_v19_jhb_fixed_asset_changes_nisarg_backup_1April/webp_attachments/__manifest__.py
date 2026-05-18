# -*- coding: utf-8 -*-
{
    'name': "WEBP Image Attachment",
    'description': """
        This odoo app helps to directly upload WEBP format image on backend(web) and frontend(website).
    """,

    "author": "Cybat",
    "website": "https://cybat.net",
    "category": "Web",
    "price": 20.00,
    "currency": 'EUR',
    'version': '19.0.1.0.0',
    'depends': ['web_editor'],
    # always loaded
    'assets': {
        'web_editor.assets_wysiwyg': [
            'static/image_widget.js',
        ],
    },
    'images': ['static/description/main_screenshot.png'],
    'application': True,
    'installable': True,
    'license': 'AGPL-3',
}
