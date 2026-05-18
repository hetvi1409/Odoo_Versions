# -*- coding: utf-8 -*-
{
    'name': "Portal Attendance",
    'description': """Portal Attendance""",
    'summary': """Portal Attendance""",
    'version': '19.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Services',
    'depends': ['web', 'portal', 'website', 'hr','hr_attendance', 'contacts','jhbproperty_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_attendance_template.xml',
        'views/hr_attendance_view.xml',
        'views/portal_attendance.xml',
    ],
    'assets': {'web.assets_frontend': [
        'portal_attendance/static/src/js/portal_checkin_message.js',
    ], },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
