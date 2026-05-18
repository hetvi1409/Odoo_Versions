{
    'name': "Attendence Update",
    'description': """Document Update""",
    'summary': """Document Update""",
    'version': '19.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '10',
    'category': 'Services',
    'depends': ['base', 'hr_attendance', 'mail', 'web','jhbproperty_base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/timesheet_approval_views.xml',
        'wizard/attendance_mail_compose_views.xml',
        'views/hr_attendence.xml',
        'data/attendence_template_data.xml',
        'data/ir_actions_server_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
    #
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
