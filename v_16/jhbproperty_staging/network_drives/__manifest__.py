{
    'name': 'Network Drives',
    'version': '16.0.1.0.0',
    "summary": "Access network drives directly from Odoo",
    "description": """
    Open network drives directly from Odoo interface.
    Features:
    Store network drive paths
    Open network drives in browser
    Easy access to shared folderss
    """,
    'author': 'Your Name',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'views/network_drive_views.xml',
        'views/drive_credential_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            '/network_drives/static/src/js/copy_path.js',
            # '/network_drives/static/src/js/network_drive_copy.js',
            '/network_drives/static/src/scss/clipboard.scss'
        ]
    },
    "external_dependencies": {"python": [
        # "pywin32",
    ]},
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}