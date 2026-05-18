{
    "name": "Bursary Application Management",
    "version": "17.0.1.0.0",
    "summary": "Manage external bursary applications, including workflow and reporting",
    "description": """
        Custom module to manage external bursary applications, including applicant data capture,
        document uploads, eligibility validation, workflow management, and reporting.
    """,
    "category": "Education/Finance",
    "author": "Your Organization",
    "website": "https://yourorganization.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "documents", "website", "survey"],
    "data": [
        'data/ir_corn_data.xml',
        'data/res_province_data.xml',
        'data/bursary_application_stage_data.xml',
        "security/ir.model.access.csv",
        # "views/website_menu.xml",
        'views/application_submit.xml',
        "views/bursary_application_views.xml",
        'views/bursary_bursary_views.xml',
        'views/bursary_programmes_views.xml',
        'views/academic_year_views.xml',
        'views/bursary_tempaltes.xml',
        'views/province_province_views.xml',
        'views/bursary_application_stage_views.xml',
        'views/survey_survey_views.xml',

        "views/bursary_menu.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            '/bursary_application/static/src/js/bursary_application.js'
        ],
        'web.assets_backend': [
            '/bursary_application/static/src/scss/bursary.scss'
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False
}