{
    'name': "Document Management",
    'description': """Document Management""",
    'summary': """Document Management""",
    'version': '18.0.1.0.0',
    'category': 'Services',
    'depends': ['documents', 'documents_hr', 'documents_hr_recruitment'],
    'data': [
        'data/document_folder.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    # 'post_init_hook': 'post_init_hook',
}
