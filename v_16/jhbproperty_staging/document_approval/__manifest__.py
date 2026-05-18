{
    'name': "Document Approval",
    'description': """Document Update""",
    'summary': """Document Update""",
    'version': '16.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '10',
    'category': 'Services',
    'depends': ['base', 'documents', 'web', 'itsys_real_estate', 'document_update'],
    'data': [
        'data/mail_template_data.xml',
        'security/ir.model.access.csv',
        'security/document_approval_groups.xml',
        'views/documents_approval_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'document_approval/static/src/js/document_inspector.js',
            'document_approval/static/src/js/document_controller.js',
            'document_approval/static/src/xml/documents_controller_mixin.xml',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
