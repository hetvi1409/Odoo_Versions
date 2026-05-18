# -*- coding: utf-8 -*-
{
    'name': "Attachment Preview",
    'summary': """
        Attachment Preview / Preview Attachment / Preview Excel / Preview Word / Preview Video / Preview PDF / Preview Image
    """,
    'description': """
        attachment preview(PDF、Excel、Word、Video、Image)
    """,
    'category': 'Website',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'category': 'Website',
    'version': '0.1',
    'license': 'OPL-1',
    'depends': ['base', 'mail'],
    'images': [
        'static/description/main_screenshot.gif'
    ],
    'assets': {
        'web.assets_backend': [
            'x2_attachment_preview/static/lib/office/docx/docx.js',
            'x2_attachment_preview/static/lib/office/docx/index.css',
            'x2_attachment_preview/static/lib/office/excel/excel.js',
            'x2_attachment_preview/static/lib/office/excel/index.css',
            'x2_attachment_preview/static/src/many2many_binary.js',
            'x2_attachment_preview/static/src/many2many_binary.xml'
        ],
    },
    'installable': True
}

