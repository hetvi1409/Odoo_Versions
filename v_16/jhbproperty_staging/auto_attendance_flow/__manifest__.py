# -*- coding: utf-8 -*-

# {
#     'name': 'Auto Attendance Flow',
#     'version': '16.0.1.0.0',
#     'category': 'Human Resources',
#     'sequence': 335,
#     "summary": "Automatically check in/out",
#     'description': """
#         Automatically check in/out
#     """,
#     'author': 'Nated Systems',
#     'company': 'Nated Systems',
#     'maintainer': 'Nated Systems',
#     'website': 'https://natedsystems.co.za/',
#     'depends': ['documents', 'hr_attendance', 'hr_holidays', 'hr_payroll','jhbproperty_base'],
#     'data': [
#         'security/ir.model.access.csv',
#         'data/attendance_cron.xml',
#         'data/payroll_data.xml',
#         'views/attendance_auto_checkout.xml',
#         # 'views/webclient_template.xml',
#         'views/attendance_view.xml',
#         'views/hr_overtime_views.xml',
#         'views/hr_employee_view.xml',
#         'wizard/attendance_report_wizard.xml',
#         'report/attendance_report.xml',
#     ],
#     'assets': {
#         'web.assets_frontend': [
#             'auto_attendance_flow/static/src/js/checkin_popup.js',
#         ],
#     },

#     'license': 'LGPL-3',
#     'installable': True,
#     'application': True,
#     'auto_install': False,
# }

{
    'name': 'Auto Attendance Flow',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'sequence': 335,
    "summary": "Automatically check in/out",
    'description': """
        Automatically check in/out
    """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': ['documents', 'hr_attendance', 'hr_holidays', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/attendance_cron.xml',
        'data/payroll_data.xml',
        'data/timesheet_generator_rule.xml',
        'views/attendance_auto_checkout.xml',
        'views/webclient_template.xml',
        'views/attendance_view.xml',
        'views/hr_overtime_views.xml',
        'views/hr_employee_view.xml',
        'views/hr_timesheet_generator_views.xml',
        'wizard/attendance_report_wizard.xml',
        'wizard/timesheet_action_wizard_view.xml',
        'wizard/signature_wizard_views.xml',
        'report/attendance_report.xml',
        'report/daily_attendance_register_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'auto_attendance_flow/static/src/scss/timesheet_generator.scss',
        ],
        'web.assets_frontend': [
            'auto_attendance_flow/static/src/js/checkin_popup.js',
        ],
    },

    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}