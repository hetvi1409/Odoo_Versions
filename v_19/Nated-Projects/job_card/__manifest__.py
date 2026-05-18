{
    'name': "Job Card",
    'description': """Job Card""",
    'summary': """Job Card""",
    'version': '16.0.1.1.0',
    'sequence': '20',
    'category': 'Project',
    'depends': ['hr', 'stock', 'project', 'hr_timesheet', 'purchase',
                'account'],
    'data': [
        'data/job_card_sequence.xml',
        'security/ir.model.access.csv',
        'views/job_cad_views.xml',
        'views/workshop_team_views.xml',
        'views/quality_check_list_views.xml',
        'views/hr_employee_views.xml',
        'views/job_card_tag_views.xml',
        'views/material_requistition_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

}
