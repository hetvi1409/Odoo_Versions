{
    "name": "Committee Management",
    "description": """Committee Management """,
    "summary": "Committee Management, Committee Process, "
               "Committee Member, Committee Evaluation, Board, Council",
    'version': '16.0.1.1.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '20',
    'category': 'Extra Tools',
    'depends': ['oi_committee', 'note', 'survey', 'documents'],
    'data': [
        'report/report_committee_meeting.xml',
        'report/report_commitee_meeting_notes.xml',
        'report/report_committee_meeting_review.xml',
        'views/committee_meeting_views.xml',
        'views/survey_survey_views.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
