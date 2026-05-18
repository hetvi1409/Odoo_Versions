{
    'name': 'OEHealth Claims',
    'version': '19.0.1.0.0',
    'summary': 'Manage Health Claims',
    'description': """
        This module helps manage medical/health insurance claims,
        including patient details, insurers, medical aid, charges,
        payments, and related actions.
    """,
    'author': 'Nated System',
    'website': 'http://www.yourcompany.com',
    'category': 'Health Management',
    'depends': ['web','base','oehealth','hr','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/claims_view.xml'
        # 'security/ir.model.access.csv',
        # 'views/claims_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oehealth_claims/static/src/claim.scss',
            'oehealth_claims/static/src/js/audio_recorder.js',
            'oehealth_claims/static/views/widget.xml'
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
