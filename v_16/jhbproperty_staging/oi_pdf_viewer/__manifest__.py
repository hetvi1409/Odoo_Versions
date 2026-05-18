# -*- coding: utf-8 -*-
{
    'name': 'PDF Viewer',
    "summary": "PDF, PDF Viewer, PDF Preview, PDF Report",
    "category": "Extra Tools",
    "version": "16.0.1.1.4",
    "license": "OPL-1",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': [
        'web',
    ],    
    'data': [
        
    ],
    'images': [
            'static/description/cover.png'
        ],
    'assets': {
        'web.assets_backend': [            
            'oi_pdf_viewer/static/src/js/pdf_controller.js',
            'oi_pdf_viewer/static/src/js/pdf_model.js',
            'oi_pdf_viewer/static/src/js/pdf_renderer.js',
            'oi_pdf_viewer/static/src/js/pdf_view.js',
            'oi_pdf_viewer/static/src/xml/templates.xml'
        ],

    },      
    'installable': True,
    'odoo-apps' : True,
    'auto_install': True,
}
