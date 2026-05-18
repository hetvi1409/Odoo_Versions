# -*- coding: utf-8 -*-
{
    'name': "Document Retention Update",
    'description': """Document Retention Update""",
    'summary': """Document Retention Update""",
    'version': '18.0.1.0.0',
    'sequence': '10',
    'category': 'Services',
    'depends': ['base', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'data/archive_cron.xml',
        'views/documents_document.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
