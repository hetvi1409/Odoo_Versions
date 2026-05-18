##############################################################################

{
    'name': 'oeHealth - QUEUE Management System',
    'version': '19.0.1.0.0',
    'author': "Braincrew Apps",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo EMR & HIS based Medical, Health and Hospital Management Solutions',
    'depends': ['oehealth', 'hr','account'],
    'price': 300.00,
    'currency': 'EUR',
    'description': """Queue Management
        """,
    "data": [
        'security/ir.model.access.csv',
        'views/queue_health_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            '/oeheath_queue/static/src/queue.scss'
        ],
    },
    }