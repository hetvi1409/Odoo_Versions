{
    'name': "Document Access Rights",
    'description': """Document Update: Access Rights""",
    'summary': """Document Update: Access Rights""",
    'version': '16.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '10',
    'category': 'Services',
    'depends': ['documents'],
    'data': [
        'security/document_access_groups.xml',
        'views/documents_folder_views.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
