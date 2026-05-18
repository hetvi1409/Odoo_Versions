{
    'name': 'Restrict Chatter Delete',
    'version': '19.0.1.0.0',
    'summary': 'Prevents deletion of log notes and messages in the chatter',
    'author': 'Custom Dev',
    'category': 'Technical',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/delete_reason_wizard_views.xml',
        'views/mail_message_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'no_chatter_delete/static/src/js/hide_delete_btn.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
