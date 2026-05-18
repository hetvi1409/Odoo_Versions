{
    'name': "Survey Report Printing",
    'description': """This module enables printing of survey reports directly from 
                      the survey results page, allowing users to easily generate and 
                      print detailed survey analysis.""",
    'summary': """Enables printing of survey reports from the survey results 
                  page.""",
    'version': '19.0.1.0.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'sequence': '10',
    'category': 'Services',
    'depends': ['survey'],
    'data': [
        'views/survey_templates_statistics.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'survey_report_printing/static/src/js/survey_result.js',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
