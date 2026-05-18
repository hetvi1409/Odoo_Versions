# -*- coding: utf-8 -*-
{
    'name': 'Log Note Customization',
    'summary': 'Prevents deletion of log notes, only admin can have access to delete it.',
    'description': """
            Restricts log note deletion for other users,
            if attempted by admin users with a required reason wizard then store the reason.
    """,
    'author': 'Hetvi Shah',
    'category': 'Discuss',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/delete_reason_wizard.xml',
        'views/message_delete_log_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'log_note_customization/static/src/js/hide_delete_action.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
