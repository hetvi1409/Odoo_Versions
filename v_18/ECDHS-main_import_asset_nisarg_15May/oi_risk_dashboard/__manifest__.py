{
    'name': 'Risk Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'author': '',
    'website': '',
    'sequence': 5,
    'summary': 'Risk Dashboard',
    'description': """
    """,
    'depends': ['web', 'oi_risk_management', 'risk_universe_update'],
    'data': [
        'views/risk_dashboard.xml'
    ],

    'assets': {
        'web.assets_backend': [
            'oi_risk_dashboard/static/src/js/dashboard.js',
            'oi_risk_dashboard/static/src/xml/dashboad.xml',
            'oi_risk_dashboard/static/src/css/dashboard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js'
        ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}
