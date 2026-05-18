# -*- coding: utf-8 -*-
{
    'name': 'Field Service Customization',
    'summary': 'Add filter on Field service calendar view',
    'description': """Add 'Assigned to' filter on Field service calendar view""",
    'author': 'Hetvi Shah',
    'category': 'Services/Field Service',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['industry_fsm'],
    'data': [
        'views/project_task.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'field_service_customization/static/src/views/fsm_calendar_model_patch.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
