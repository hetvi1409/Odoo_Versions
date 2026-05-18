
{
    'name': 'Governance',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'author': 'Cyder Solutions',
    'website': 'https://www.cyder.com.au/',
    'price': '30.0',
    'currency': 'USD',
    'sequence': -65,
    'summary': 'Business Governance',
    'description': """
    Business Governace
    Startegy -> Goals -> Objectives -> Projects
    Registers
        - Risk
        - Challenges
    """,
    'depends': ['mail', 'project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/challenge_sequence.xml',
        'data/risk_sequence.xml',
        'data/strategy_sequence.xml',
        'data/goal_sequence.xml',
        'data/objective_sequence.xml',
        'data/problem_sequence.xml',
        'data/cause_sequence.xml',
        'views/menu.xml',
        'views/risk_view.xml',
        'views/challenges_view.xml',
        'views/risk_category_view.xml',
        'views/strategy_view.xml',
        'views/challenges_tag_view.xml',
        'views/goals_view.xml',
        'views/objectives_view.xml',
        'views/problem_view.xml',
        'views/action_log_view.xml',
        'views/root_cause_view.xml',
        'report/report.xml',
        'report/goals_report.xml',
        'report/objectives_report.xml',
        'report/strategy_report.xml',
        'report/risk_report.xml',
        'report/challenge_report.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'governance/static/src/css/app_menu_wrap.css',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1'
    }
